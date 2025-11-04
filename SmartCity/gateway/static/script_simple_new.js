console.log("[APP] Script iniciado")

const API_BASE = "/api"
let currentRegiao = null
let regioesList = []
let detailModal = null
let regioesModal = null
let intervaloId;

function iniciarAtualizacao(tabName) {
  if (!intervaloId) {
    if(tabName == 'semaforos'){
      intervaloId = setInterval(() => {
        carregarSemaforos();
      }, 1000);
    }else if(tabName == 'postes'){
      intervaloId = setInterval(() => {
        carregarPostes();
      }, 1000);
    }
  }
}

function pararAtualizacao() {
  clearInterval(intervaloId);
  intervaloId = null;
}

function switchTab(tabName) {
  document.querySelectorAll(".tab-content").forEach(tab => tab.style.display = "none")
  document.querySelectorAll(".nav-link").forEach(btn => btn.classList.remove("active"))
  document.getElementById(`${tabName}-tab`).style.display = "block"
  event.target.classList.add("active")
  pararAtualizacao()
  iniciarAtualizacao(tabName)
}

function logout() {
  if (confirm("Tem certeza?")) window.location.href = "/logout"
}

function showAddRegiao() {
  if (!regioesModal) {
    regioesModal = new bootstrap.Modal(document.getElementById("regiao-modal"))
  }
  regioesModal.show()
}

function closeModal() {
  document.getElementById("regiao-nome").value = ""
  document.getElementById("regiao-descricao").value = ""
  if (regioesModal) regioesModal.hide()
}

function closeDetailModal() {
  if (detailModal) detailModal.hide()
}

async function carregarRegioes() {
  console.log("[LOAD] Carregando regiões...")
  try {
    const resp = await fetch("/regioes")
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    
    const regioes = await resp.json()
    regioesList = regioes
    console.log("[LOAD] Carregadas:", regioes.length)
    
    const html = regioes.map(r => `
      <button type="button" class="list-group-item list-group-item-action list-group-item-dark text-light border-info-subtle" onclick="selecionarRegiao(${r.id}, event)">
        <strong>${r.nome}</strong>
        ${r.descricao ? `<p class="mb-0 small text-muted">${r.descricao}</p>` : ''}
      </button>
    `).join("")
    
    document.getElementById("regioes-list").innerHTML = html || "<p class='text-muted'>Nenhuma região</p>"
  } catch (e) {
    console.error("[LOAD] Erro:", e)
  }
}

async function criarRegiao() {
  const nome = document.getElementById("regiao-nome").value.trim()
  const descricao = document.getElementById("regiao-descricao").value.trim()
  if (!nome) return alert("Nome obrigatório")
  try {
    const resp = await fetch("/add_regiao", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, descricao }),
    })
    if (resp.ok) {
      closeModal()
      carregarRegioes()
    }
  } catch (e) {
    console.error(e)
  }
}

async function selecionarRegiao(regiaoId, evt) {
  try {
    const resp = await fetch(`/regioes/${regiaoId}`)
    const regiao = await resp.json()
    currentRegiao = regiao
    document.querySelectorAll(".list-group-item-action").forEach(item => item.classList.remove("active"))
    if (evt && evt.target) evt.target.closest(".list-group-item-action").classList.add("active")
    carregarSemaforos()
    carregarPostes()
    atualizarDashboard()
  } catch (e) {
    console.error(e)
  }
}

function adicionarSemaforo() {
  if (!currentRegiao) {
    alert("Selecione uma região")
    return
  }
  
  const localizacao = document.getElementById("semaforoLocalizacao").value.trim()
  const tempo = document.getElementById("semaforoTempo").value
  
  if (!localizacao || !tempo) {
    alert("Preencha todos os campos")
    return
  }
  
  fetch("/add_semaforo", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      regiao_id: currentRegiao.id,
      localizacao,
      estado: "verde",
      tempo: parseInt(tempo)
    })
  }).then(resp => {
    if (resp.ok) {
      document.getElementById("semaforoLocalizacao").value = ""
      document.getElementById("semaforoTempo").value = ""
      carregarSemaforos()
      atualizarDashboard()
      alert("Semáforo criado!")
    }
  }).catch(e => console.error(e))
}

function adicionarPoste() {
  if (!currentRegiao) {
    alert("Selecione uma região")
    return
  }
  
  const localizacao = document.getElementById("posteLocalizacao").value.trim()
  if (!localizacao) {
    alert("Preencha a localização")
    return
  }
  
  const automatico = document.getElementById("posteAutomatico")?.checked ? 1 : 0
  
  fetch("/add_poste", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      regiao_id: currentRegiao.id,
      localizacao,
      estado: 1,
      automatico: automatico
    })
  }).then(resp => {
    if (resp.ok) {
      document.getElementById("posteLocalizacao").value = ""
      document.getElementById("posteAutomatico").checked = false
      carregarPostes()
      atualizarDashboard()
      alert("Poste criado!")
    }
  }).catch(e => console.error(e))
}

function carregarSemaforos() {
  if (!currentRegiao) {
    document.getElementById("semaforos-list").innerHTML = "<p class='text-muted'>Selecione uma região</p>"
    return
  }
  fetch(`/semaforos?regiao_id=${currentRegiao.id}`)
    .then(r => r.json())
    .then(semaforos => {
      const html = semaforos.map(s => {
        const tempo = (Math.abs(Math.floor(((new Date(s.created_at) - new Date())) / 1000)) % s.tempo) / s.tempo;
        const estado = tempo < 0.5 ? 'verde' : tempo < 0.65 ? 'amarelo' : 'vermelho';
        const corEstado = estado === 'verde' ? 'success' : estado === 'vermelho' ? 'danger' : 'warning'
        return `
        <a href="#" onclick="mostrarDetalheSemaforo(${s.id}); return false;" class="list-group-item list-group-item-action list-group-item-dark text-light border-secondary">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h6 class="mb-1">📍 ${s.localizacao}</h6>
              <p class="mb-0 small text-muted">
                Estado: <span class="badge bg-${corEstado}">${estado}</span>
                Tempo: ${s.tempo}s
                Eficiência: <span class="badge bg-${s.eficiencia >= 70 ? 'success' : s.eficiencia >= 50 ? 'warning' : 'danger'}">${s.eficiencia}%</span>
              </p>
            </div>
            <button onclick="deletarSemaforo(${s.id}, event)" class="btn btn-danger btn-sm" title="Deletar">🗑️</button>
          </div>
        </a>
      `}).join("")
      document.getElementById("semaforos-list").innerHTML = html || "<p class='text-muted p-3'>Nenhum semáforo</p>"
    })
    .catch(e => console.error(e))
}

function carregarPostes() {
  if (!currentRegiao) {
    document.getElementById("postes-list").innerHTML = "<p class='text-muted'>Selecione uma região</p>"
    return
  }
  
  fetch(`/postes?regiao_id=${currentRegiao.id}`)
    .then(r => r.json())
    .then(postes => {
      const html = postes.map(p => `
        <a href="#" onclick="mostrarDetalhePoste(${p.id}); return false;" class="list-group-item list-group-item-action list-group-item-dark text-light border-secondary">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h6 class="mb-1">💡 ${p.localizacao}</h6>
              <p class="mb-0 small text-muted">
                Estado: ${p.estado ? "<span class='badge bg-success'>Ligado</span>" : "<span class='badge bg-secondary'>Desligado</span>"}
                Automático: ${p.automatico ? "✓" : "✗"}
                Eficiência: <span class="badge bg-${p.eficiencia >= 70 ? 'success' : p.eficiencia >= 50 ? 'warning' : 'danger'}">${p.eficiencia}%</span>
              </p>
            </div>
            <button onclick="deletarPoste(${p.id}, event)" class="btn btn-danger btn-sm" title="Deletar">🗑️</button>
          </div>
        </a>
      `).join("")
      document.getElementById("postes-list").innerHTML = html || "<p class='text-muted p-3'>Nenhum poste</p>"
    })
    .catch(e => console.error(e))
}

function deletarSemaforo(id, evt) {
  if (evt) evt.stopPropagation()
  fetch(`/semaforos/${id}`, { method: "DELETE" })
    .then(() => {
      carregarSemaforos()
      atualizarDashboard()
    })
    .catch(e => console.error(e))
}

function deletarPoste(id, evt) {
  if (evt) evt.stopPropagation()
  fetch(`/postes/${id}`, { method: "DELETE" })
    .then(() => {
      carregarPostes()
      atualizarDashboard()
    })
    .catch(e => console.error(e))
}

function mostrarDetalheSemaforo(id) {
  fetch(`/get_semaforo/${id}`)
    .then(r => r.json())
    .then(semaforo => {
      const tempo = (Math.abs(Math.floor(((new Date(semaforo.created_at) - new Date())) / 1000)) % semaforo.tempo) / semaforo.tempo;
      const estado = tempo < 0.5 ? 'verde' : tempo < 0.65 ? 'amarelo' : 'vermelho';
        const html = `
        <h5 class="mb-3">🚦 Detalhes do Semáforo</h5>
        <div class="list-group list-group-flush">
          <div class="list-group-item bg-dark border-secondary">
            <strong>Localização:</strong> ${semaforo.localizacao}
          </div>
          <div class="list-group-item bg-dark border-secondary">
            <strong>Estado:</strong> ${estado}
          </div>
          <div class="list-group-item bg-dark border-secondary">
            <strong>Tempo:</strong> ${semaforo.tempo}s
          </div>
          <div class="list-group-item bg-dark border-secondary">
            <strong>Eficiência:</strong> <span class="badge bg-warning text-dark">${semaforo.eficiencia}%</span>
          </div>
        </div>
        <div class="d-flex gap-2 mt-3">
          <button onclick="deletarSemaforoModal(${semaforo.id})" class="btn btn-danger btn-sm flex-grow-1">🗑️ Deletar</button>
          <button onclick="closeDetailModal()" class="btn btn-secondary btn-sm flex-grow-1">Fechar</button>
        </div>
      `
      document.getElementById("detail-content").innerHTML = html
      if (!detailModal) {
        detailModal = new bootstrap.Modal(document.getElementById("detail-modal"))
      }
      detailModal.show()
    })
    .catch(e => console.error(e))
}

function mostrarDetalhePoste(id) {
  fetch(`/get_poste/${id}`)
    .then(r => r.json())
    .then(poste => {
      const html = `
        <h5 class="mb-3">💡 Detalhes do Poste</h5>
        <div class="list-group list-group-flush">
          <div class="list-group-item bg-dark border-secondary">
            <strong>Localização:</strong> ${poste.localizacao}
          </div>
          <div class="list-group-item bg-dark border-secondary">
            <strong>Estado:</strong> ${poste.estado ? "Ligado" : "Desligado"}
          </div>
          <div class="list-group-item bg-dark border-secondary">
            <strong>Automático:</strong> ${poste.automatico ? "Sim" : "Não"}
          </div>
          <div class="list-group-item bg-dark border-secondary">
            <strong>Eficiência:</strong> <span class="badge bg-warning text-dark">${poste.eficiencia}%</span>
          </div>
        </div>
        <div class="d-flex gap-2 mt-3">
          <button onclick="deletarPosteModal(${poste.id})" class="btn btn-danger btn-sm flex-grow-1">🗑️ Deletar</button>
          <button onclick="closeDetailModal()" class="btn btn-secondary btn-sm flex-grow-1">Fechar</button>
        </div>
      `
      document.getElementById("detail-content").innerHTML = html
      if (!detailModal) {
        detailModal = new bootstrap.Modal(document.getElementById("detail-modal"))
      }
      detailModal.show()
    })
    .catch(e => console.error(e))
}

function deletarSemaforoModal(id) {
  if (confirm("Tem certeza que deseja deletar este semáforo?")) {
    deletarSemaforo(id)
    closeDetailModal()
  }
}

function deletarPosteModal(id) {
  if (confirm("Tem certeza que deseja deletar este poste?")) {
    deletarPoste(id)
    closeDetailModal()
  }
}

async function atualizarDashboard() {
  if (!currentRegiao) return
  
  Promise.all([
    fetch(`/semaforos?regiao_id=${currentRegiao.id}`).then(r => r.json()),
    fetch(`/postes?regiao_id=${currentRegiao.id}`).then(r => r.json())
  ]).then(([semaforos, postes]) => {
    document.getElementById("region-selected").style.display = "none"
    document.getElementById("dashboard-content").style.display = "block"
    
    document.getElementById("total-semaforos").textContent = semaforos.length
    document.getElementById("total-postes").textContent = postes.length
    
    const efSem = semaforos.length > 0 ? Math.round(semaforos.reduce((a,b) => a + (b.eficiencia || 0), 0) / semaforos.length) : 0
    const efPos = postes.length > 0 ? Math.round(postes.reduce((a,b) => a + (b.eficiencia || 0), 0) / postes.length) : 0
    
    document.getElementById("eficiencia-semaforos").textContent = efSem + "%"
    document.getElementById("eficiencia-postes").textContent = efPos + "%"
    
    const topSemaforosEficientes = semaforos.sort((a, b) => (b.eficiencia || 0) - (a.eficiencia || 0)).slice(0, 5)
    const htmlTopSemEficientes = topSemaforosEficientes.map((s, i) => `
      <a href="#" onclick="mostrarDetalheSemaforo(${s.id}); return false;" class="list-group-item list-group-item-action list-group-item-dark text-light border-secondary">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <span class="badge bg-info me-2">#${i+1}</span>
            <strong>${s.localizacao}</strong>
          </div>
          <span class="badge bg-success">${s.eficiencia || 0}%</span>
        </div>
      </a>
    `).join("")
    document.getElementById("top-semaforos-eficientes").innerHTML = htmlTopSemEficientes || "<p class='text-muted p-3'>Nenhum semáforo</p>"
    
    const topSemaforosIneficientes = semaforos.sort((a, b) => (a.eficiencia || 0) - (b.eficiencia || 0)).slice(0, 5)
    const htmlTopSemIneficientes = topSemaforosIneficientes.map((s, i) => `
      <a href="#" onclick="mostrarDetalheSemaforo(${s.id}); return false;" class="list-group-item list-group-item-action list-group-item-dark text-light border-secondary">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <span class="badge bg-info me-2">#${i+1}</span>
            <strong>${s.localizacao}</strong>
          </div>
          <span class="badge bg-danger">${s.eficiencia || 0}%</span>
        </div>
      </a>
    `).join("")
    document.getElementById("top-semaforos-ineficientes").innerHTML = htmlTopSemIneficientes || "<p class='text-muted p-3'>Nenhum semáforo</p>"
    
    const topPostesEficientes = postes.sort((a, b) => (b.eficiencia || 0) - (a.eficiencia || 0)).slice(0, 5)
    const htmlTopPosEficientes = topPostesEficientes.map((p, i) => `
      <a href="#" onclick="mostrarDetalhePoste(${p.id}); return false;" class="list-group-item list-group-item-action list-group-item-dark text-light border-secondary">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <span class="badge bg-info me-2">#${i+1}</span>
            <strong>${p.localizacao}</strong>
          </div>
          <span class="badge bg-success">${p.eficiencia || 0}%</span>
        </div>
      </a>
    `).join("")
    document.getElementById("top-postes-eficientes").innerHTML = htmlTopPosEficientes || "<p class='text-muted p-3'>Nenhum poste</p>"
    
    const topPostesIneficientes = postes.sort((a, b) => (a.eficiencia || 0) - (b.eficiencia || 0)).slice(0, 5)
    const htmlTopPosIneficientes = topPostesIneficientes.map((p, i) => `
      <a href="#" onclick="mostrarDetalhePoste(${p.id}); return false;" class="list-group-item list-group-item-action list-group-item-dark text-light border-secondary">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <span class="badge bg-info me-2">#${i+1}</span>
            <strong>${p.localizacao}</strong>
          </div>
          <span class="badge bg-danger">${p.eficiencia || 0}%</span>
        </div>
      </a>
    `).join("")
    document.getElementById("top-postes-ineficientes").innerHTML = htmlTopPosIneficientes || "<p class='text-muted p-3'>Nenhum poste</p>"
    
  }).catch(e => console.error(e))
}

async function criarDadosMock() {
  console.log("[MOCK] Verificando dados...")
  
  try {
    const respRegioes = await fetch("/regioes")
    const regioes = await respRegioes.json()
    
    if (regioes.length > 0) {
      console.log("[MOCK] Regiões já existem, pulando criação")
      return
    }
    
    console.log("[MOCK] Criando regiões...")
    
    const regioesData = [
      { nome: "Centro da Cidade", descricao: "Região central com alta movimentação e tráfego intenso" },
      { nome: "Vila Mariana", descricao: "Área residencial e comercial ao sul da cidade" },
      { nome: "Pinheiros", descricao: "Região oeste, zona de negócios e finanças" }
    ]
    
    const regioesIds = []
    for (const reg of regioesData) {
      const resp = await fetch("/add_regiao", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reg)
      })
      if (resp.ok) console.log("[MOCK] Região criada:", reg.nome)
    }
    
    const respRegioesAtualizado = await fetch("/regioes")
    const regioesAtualizado = await respRegioesAtualizado.json()
    
    const mockData = {
      "Centro da Cidade": {
        semaforos: [
          { localizacao: "Av. Paulista x Rua Augusta", estado: "verde", tempo: 60 },
          { localizacao: "Rua 25 de Março x Rua São Bento", estado: "vermelho", tempo: 45 },
          { localizacao: "Av. Rio Branco x Rua Tatuapé", estado: "amarelo", tempo: 55 },
          { localizacao: "Av. Consolação x Av. Paulista", estado: "verde", tempo: 50 },
          { localizacao: "Rua Barão de Itapetininga x Rua Augusta", estado: "verde", tempo: 65 }
        ],
        postes: [
          { localizacao: "Av. Paulista, nº 1000", automatico: 1 },
          { localizacao: "Rua 25 de Março, nº 500", automatico: 0 },
          { localizacao: "Av. Consolação, nº 2000", automatico: 1 },
          { localizacao: "Largo do Arouche, nº 100", automatico: 1 },
          { localizacao: "Rua Barão de Itapetininga, nº 250", automatico: 0 }
        ]
      },
      "Vila Mariana": {
        semaforos: [
          { localizacao: "Av. Santo Amaro x Rua Bandeira", estado: "verde", tempo: 55 },
          { localizacao: "Rua Vergueiro x Rua Dr. Bacelar", estado: "amarelo", tempo: 50 },
          { localizacao: "Av. Domingos de Morais x Rua Abílio Soares", estado: "verde", tempo: 60 },
          { localizacao: "Rua Pedroso x Rua Pio IV", estado: "vermelho", tempo: 48 },
          { localizacao: "Av. Imigrantes x Rua Dr. Antenor Duarte", estado: "verde", tempo: 65 }
        ],
        postes: [
          { localizacao: "Av. Santo Amaro, nº 3000", automatico: 1 },
          { localizacao: "Rua Vergueiro, nº 1500", automatico: 1 },
          { localizacao: "Av. Domingos de Morais, nº 2500", automatico: 0 },
          { localizacao: "Rua Pedroso, nº 800", automatico: 0 },
          { localizacao: "Av. Imigrantes, nº 4000", automatico: 1 }
        ]
      },
      "Pinheiros": {
        semaforos: [
          { localizacao: "Av. Faria Lima x Rua Iracema", estado: "verde", tempo: 65 },
          { localizacao: "Rua Bandeira x Rua Bom Jesus", estado: "verde", tempo: 58 },
          { localizacao: "Av. Pedroso de Morais x Rua Funchal", estado: "amarelo", tempo: 52 },
          { localizacao: "Rua Doutor Mário Ferraz x Av. Faria Lima", estado: "vermelho", tempo: 50 },
          { localizacao: "Av. Rebouças x Rua Funcionários", estado: "verde", tempo: 60 }
        ],
        postes: [
          { localizacao: "Av. Faria Lima, nº 2800", automatico: 1 },
          { localizacao: "Rua Bandeira, nº 1200", automatico: 1 },
          { localizacao: "Av. Pedroso de Morais, nº 1900", automatico: 0 },
          { localizacao: "Rua Doutor Mário Ferraz, nº 1100", automatico: 1 },
          { localizacao: "Av. Rebouças, nº 2100", automatico: 0 }
        ]
      }
    }
    
    for (const regiao of regioesAtualizado) {
      const dados = mockData[regiao.nome]
      if (!dados) continue
      
      console.log(`[MOCK] Criando dados para ${regiao.nome}...`)
      
      for (const sem of dados.semaforos) {
        await fetch("/add_semaforo", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            regiao_id: regiao.id,
            ...sem
          })
        })
      }
      
      for (const pos of dados.postes) {
        await fetch("/add_poste", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            regiao_id: regiao.id,
            estado: 1,
            ...pos
          })
        })
      }
    }
    
    console.log("[MOCK] Dados criados com sucesso!")
  } catch (e) {
    console.error("[MOCK] Erro ao criar dados:", e)
  }
}

async function inicializar() {
  console.log("[INIT] Verificando autenticação...")
  try {
    const resp = await fetch("/api/auth-status")
    if (!resp.ok) {
      console.log("[INIT] Não autenticado, redirecionando...")
      window.location.href = "/"
      return
    }
    console.log("[INIT] Autenticado, carregando...")
    
    await criarDadosMock()
    await carregarRegioes()
    console.log("[INIT] Pronto!")
  } catch (e) {
    console.error("[INIT] Erro:", e)
    window.location.href = "/"
  }
}

console.log("[APP] DOM:", document.readyState)
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", inicializar)
} else {
  setTimeout(inicializar, 50)
}
