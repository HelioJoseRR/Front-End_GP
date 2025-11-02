console.log("[APP] Script iniciado")

const API_BASE = "/api"
let currentRegiao = null
let regioesList = []

function switchTab(tabName) {
  document.querySelectorAll(".tab-content").forEach(tab => tab.classList.remove("active"))
  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"))
  document.getElementById(`${tabName}-tab`).classList.add("active")
  event.target.classList.add("active")
}

function logout() {
  if (confirm("Tem certeza que deseja sair?")) {
    window.location.href = "/logout"
  }
}

function showAddRegiao() {
  document.getElementById("regiao-modal").style.display = "block"
}

function closeModal() {
  document.getElementById("regiao-modal").style.display = "none"
  document.getElementById("regiao-nome").value = ""
  document.getElementById("regiao-descricao").value = ""
}

function closeDetailModal() {
  document.getElementById("detail-modal").style.display = "none"
}

window.onclick = function(event) {
  const modal = document.getElementById("regiao-modal")
  const detailModal = document.getElementById("detail-modal")
  if (event.target == modal) modal.style.display = "none"
  if (event.target == detailModal) detailModal.style.display = "none"
}

async function carregarRegioes() {
  console.log("[REGIOES] Carregando...")
  try {
    const resp = await fetch("/regioes")
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    
    const regioes = await resp.json()
    regioesList = regioes
    console.log("[REGIOES] Carregadas:", regioes.length)
    
    const html = regioes.map(r => `
      <div class="regiao-item" onclick="selecionarRegiao(${r.id}, event)">
        <strong>${r.nome}</strong>
        ${r.descricao ? `<p>${r.descricao}</p>` : ''}
      </div>
    `).join("")
    
    document.getElementById("regioes-list").innerHTML = html || "<p>Nenhuma região</p>"
  } catch (e) {
    console.error("[REGIOES] Erro:", e)
    document.getElementById("regioes-list").innerHTML = "<p>Erro ao carregar regiões</p>"
  }
}

async function criarRegiao() {
  const nome = document.getElementById("regiao-nome").value.trim()
  const descricao = document.getElementById("regiao-descricao").value.trim()
  if (!nome) {
    alert("Nome é obrigatório")
    return
  }
  try {
    const resp = await fetch("/add_regiao", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, descricao }),
    })
    if (resp.ok) {
      alert("Região criada!")
      closeModal()
      carregarRegioes()
    } else {
      alert("Erro ao criar região")
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
    document.querySelectorAll(".regiao-item").forEach(item => item.classList.remove("active"))
    if (evt) evt.target.closest(".regiao-item").classList.add("active")
  } catch (e) {
    console.error(e)
  }
}

function adicionarSemaforo() {
  alert("Funcionalidade em desenvolvimento")
}

function adicionarPoste() {
  alert("Funcionalidade em desenvolvimento")
}

async function inicializar() {
  console.log("[INIT] Sistema inicializando...")
  await carregarRegioes()
  console.log("[INIT] Pronto!")
}

// Executar
console.log("[APP] DOM state:", document.readyState)
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", inicializar)
} else {
  setTimeout(inicializar, 50)
}
console.log("[APP] Script finalizado")
