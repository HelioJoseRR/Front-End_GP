const API_BASE = "/api";
let modoIluminacao = "normal";

function criarEstrelas(quantidade) {
    const estrelasContainer = document.createElement('div');
    estrelasContainer.classList.add('estrelas-container');
    document.body.appendChild(estrelasContainer);

    for (let i = 0; i < quantidade; i++) {
        const estrela = document.createElement('div');
        estrela.classList.add('estrela');
        
        const estrelaSize = 20;
        
        const x = Math.random() * (window.innerWidth - estrelaSize);
        const y = Math.random() * (window.innerHeight - estrelaSize);
        estrela.style.left = `${x}px`;
        estrela.style.top = `${y}px`;
        
        const duracao = Math.random() * 3 + 2; 
        const atraso = Math.random() * 5; 
        estrela.style.animationDuration = `${duracao}s`;
        estrela.style.animationDelay = `${atraso}s`;
        
        estrelasContainer.appendChild(estrela);
    }
}

function atualizarCiclo(){
    const body = document.body;
    const sol = document.querySelector('.sol');
    const lua = document.querySelector('.lua');
    const nuvens = document.querySelector('.nuvens');
    const estrelasContainer = document.querySelector('.estrelas-container');

    if (estrelasContainer) {
        estrelasContainer.remove();
    }
    if (nuvens) nuvens.style.opacity = '0';

    body.classList.remove("dia", "noite", "amanhecer", "entardecer");

    cicloDiaNoite.indiceAtual = (cicloDiaNoite.indiceAtual + 1) % cicloDiaNoite.estados.length;
    cicloDiaNoite.estadoAtual = cicloDiaNoite.estados[cicloDiaNoite.indiceAtual];

    body.classList.add(cicloDiaNoite.estadoAtual);

    switch(cicloDiaNoite.estadoAtual) {
        case "amanhecer":
            if (sol) sol.style.opacity = '0';
            if (lua) lua.style.opacity = '0';
            if (nuvens) nuvens.style.opacity = '1';
            break;
        case "dia":
            if (sol) sol.style.opacity = '1';
            if (lua) lua.style.opacity = '0';
            if (nuvens) nuvens.style.opacity = '1';
            break;
        case "entardecer":
            if (sol) sol.style.opacity = '1';
            if (lua) lua.style.opacity = '0';
            if (nuvens) nuvens.style.opacity = '1';
            break;
        case "noite":
            if (sol) sol.style.opacity = '0';
            if (lua) lua.style.opacity = '1';
            if (nuvens) nuvens.style.opacity = '0';
            criarEstrelas(200);
            break;
    }
}

function atualizarSemaforo(estado){
    const luzes = {
        vermelho: document.getElementById("luz-vermelha"),
        amarelo: document.getElementById("luz-amarelo"),
        verde: document.getElementById("luz-verde")
    };

    Object.values(luzes).forEach(l => {
        l.classList.remove("acesa", "piscando");
    });

    if (estado === "vermelho")
    {
        luzes.vermelho.classList.add("acesa");
    }
    else if (estado === "verde")
    {
        luzes.verde.classList.add("acesa");
    }
    else if (estado === "amarelo")
    {
        luzes.amarelo.classList.add("acesa");
    }
    else if (estado === "intermitente")
    {
        luzes.amarelo.classList.add("acesa", "piscando");
    }

    document.getElementById("estadoSemaforo").innerText = "Semáforo: " + estado;
}

function atualizarPoste() {
    const luzPoste = document.getElementById("luz-poste");

    luzPoste.classList.remove("acesa", "piscando", "desligado");

    if (modoIluminacao === "normal") {
        if (cicloDiaNoite.estadoAtual === "noite") {
            luzPoste.classList.add("acesa");
        } else {
            luzPoste.classList.add("desligado");
        }
    } 
    else if (modoIluminacao === "falha") {
        luzPoste.classList.add("acesa", "piscando");
    } 
    else if (modoIluminacao === "manutenção" || modoIluminacao === "desligar") {
        luzPoste.classList.add("desligado");
    }
    else if(modoIluminacao === "ligar"){
        luzPoste.classList.add("acesa");
    }
}


let cicloDiaNoite ={
    estados: [ "amanhecer", "dia", "entardecer", "noite"],
    indiceAtual: 0,
    estadoAtual: "amanhecer"
}

async function atualizarEstados(){
    try{
        let semaforoResp = await fetch(`${API_BASE}/semaforo`);
        let semaforoData = await semaforoResp.json();
        atualizarSemaforo(semaforoData.dados.semaforo);

        try {
            let modoResp = await fetch(`${API_BASE}/iluminacao/modo`);
            if (modoResp.ok) {
                let modoJson = await modoResp.json();
                if (modoJson.modo) {
                    modoIluminacao = modoJson.modo;
                } else if (modoJson.dados && modoJson.dados.modo) {
                    modoIluminacao = modoJson.dados.modo;
                }
            } else {
                console.warn("Não foi possível obter modo da iluminação (status):", modoResp.status);
            }
        } catch (e) {
            console.warn("Erro ao buscar modo da iluminação:", e);
        }

        atualizarPoste(); 

        document.getElementById("estadoIluminacao").innerText = "Iluminação: " + modoIluminacao; 

    } catch (e) {
        console.error("Erro ao atualizar estados", e);
    }
}


async function alterarModoSemaforo(modo) {
    try{
        let resp = await fetch(`${API_BASE}/semaforo/modo`,{
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({modo})
        });

        let data = await resp.json();
        console.log("Resposta semaforo", data);
        atualizarEstados();
    }
    catch(e){
        console.error("Erro ao alterar modo da iluminação:", e);
    }
}

async function alterarModoIluminacao(modo) {
    modoIluminacao = modo;
    try{
        let resp = await fetch(`${API_BASE}/iluminacao/modo`,{
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({modo})
        });

        let data = await resp.json();
        console.log("Resposta iluminacao", data);

        atualizarEstados();
    }
    catch(e){
        console.error("Erro ao alterar modo da iluminação:", e);
    }
}

setInterval(atualizarEstados, 2000);
atualizarEstados();
setInterval(atualizarCiclo, 30000);
atualizarCiclo();