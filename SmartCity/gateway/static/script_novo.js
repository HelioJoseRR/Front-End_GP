// ========== VARIÁVEIS GLOBAIS ==========
const API_BASE = "/api"
let currentRegiao = null
let regioesList = []

// ========== FUNÇÕES BÁSICAS ==========
function switchTab(tabName) {
  document.querySelectorAll(".tab-content").forEach(tab => {
    tab.classList.remove("active")
  })
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.remove("active")
  })
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

// ========== CARREGAMENTO DE REGIÕES ==========
async function carregarRegioes() {
  try {
    console.log("[LOAD] Carregando regiões...")
    const resp = await fetch("/regioes")
    console.log("[LOAD] Status:", resp.status)
    
    if (!resp.ok) {
      console.error("[LOAD] Erro:", resp.status)
      return
    }
    
    const regioes = await resp.json()
    console.log("[LOAD] Regiões recebidas:", regioes.length)
    regioesList = regioes
    
    const html = regioes.map(r => `
      <div class="regiao-item" onclick="selecionarRegiao(${r.id})">
        <strong>${r.nome}</strong>
        ${r.descricao ? `<p>${r.descricao}</p>` : ''}
      </div>
    `).join("")
    
    const container = document.getElementById("regioes-list")
    if (container) {
      container.innerHTML = html || "<p>Nenhuma região</p>"
      console.log("[LOAD] Regiões renderizadas")
    }
  } catch (e) {
    console.error("[LOAD] Erro fatal:", e)
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
    }
  } catch (e) {
    console.error(e)
  }
}

async function selecionarRegiao(regiaoId) {
  try {
    const resp = await fetch(`/regioes/${regiaoId}`)
    const regiao = await resp.json()
    currentRegiao = regiao
    console.log("[SELECT] Região selecionada:", regiao.nome)
  } catch (e) {
    console.error(e)
  }
}

// ========== INICIALIZAÇÃO ==========
async function inicializar() {
  console.log("[INIT] Iniciando...")
  await carregarRegioes()
  console.log("[INIT] Pronto!")
}

// ========== EXECUÇÃO ==========
console.log("[START] Script carregado, DOM state:", document.readyState)

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    console.log("[START] DOMContentLoaded")
    inicializar()
  })
} else {
  console.log("[START] DOM já pronto")
  inicializar()
}
