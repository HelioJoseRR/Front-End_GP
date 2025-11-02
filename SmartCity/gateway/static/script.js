console.log("[APP] Script iniciado")

const API_BASE = "/api"
let currentRegiao = null
let regioesList = []
let mockDataInitialized = false
let currentEditSemaforoId = null
let currentEditPosteId = null

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

async function carregarRegioes() {
  try {
    console.log("Iniciando carregamento de regiões...")
    const resp = await fetch("/regioes")
    console.log("Resposta recebida:", resp.status, resp.statusText)
    
    if (!resp.ok) {
      if (resp.status === 401 || resp.status === 302) {
        console.log("Não autenticado, redirecionando para logout")
        window.location.href = "/logout"
        return
      }
      throw new Error(`HTTP ${resp.status} ${resp.statusText}`)
    }
    
    const regioes = await resp.json()
    console.log("Regiões carregadas com sucesso:", regioes.length, "itens")
    regioesList = regioes
    
    const listHTML = regioes.map(r => `
      <div class="regiao-item ${currentRegiao?.id === r.id ? 'active' : ''}" onclick="selecionarRegiao(${r.id}, event)">
        <strong>${r.nome}</strong>
        ${r.descricao ? `<p>${r.descricao}</p>` : ''}
      </div>
    `).join("")
    
    const container = document.getElementById("regioes-list")
    if (container) {
      container.innerHTML = listHTML || "<p>Nenhuma região criada</p>"
      console.log("Regiões renderizadas com sucesso")
    } else {
      console.error("Elemento regioes-list não encontrado no DOM")
    }
  } catch (e) {
    console.error("Erro ao carregar regiões:", e)
    const container = document.getElementById("regioes-list")
    if (container) {
      container.innerHTML = "<p class='error'>Erro: " + e.message + "</p>"
    }
  }
}

async function criarRegiao() {
  const nome = document.getElementById("regiao-nome").value.trim()
  const descricao = document.getElementById("regiao-descricao").value.trim()
  
  if (!nome) {
    alert("⚠️ Nome da região é obrigatório")
    return
  }
  
  try {
    const resp = await fetch("/add_regiao", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, descricao }),
    })
    
    if (resp.ok) {
      alert("✅ Região criada com sucesso!")
      closeModal()
      carregarRegioes()
    } else {
      alert("❌ Erro ao criar região")
    }
  } catch (e) {
    console.error("Erro:", e)
    alert("❌ Erro na comunicação")
  }
}

async function selecionarRegiao(regiaoId, evt) {
  try {
    const resp = await fetch(`/regioes/${regiaoId}`)
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}`)
    }
    const regiao = await resp.json()
    currentRegiao = regiao
    
    document.querySelectorAll(".regiao-item").forEach(item => item.classList.remove("active"))
    if (evt && evt.target) {
      evt.target.closest(".regiao-item").classList.add("active")
    } else {
      document.querySelector(`.regiao-item[onclick*="${regiaoId}"]`)?.classList.add("active")
    }
    
    await atualizarDashboard()
  } catch (e) {
    console.error("Erro ao selecionar região:", e)
    alert("❌ Erro ao selecionar região")
  }
}

async function atualizarDashboard() {
  if (!currentRegiao) return
  
  try {
    const [respSemaforos, respPostes, respTop5SemaforosEficientes, respTop5SemaforosIneficientes, respTop5PostesEficientes, respTop5PostesIneficientes] = await Promise.all([
      fetch(`/semaforos?regiao_id=${currentRegiao.id}`),
      fetch(`/postes?regiao_id=${currentRegiao.id}`),
      fetch(`/semaforos/top5/${currentRegiao.id}/eficientes`),
      fetch(`/semaforos/top5/${currentRegiao.id}/ineficientes`),
      fetch(`/postes/top5/${currentRegiao.id}/eficientes`),
      fetch(`/postes/top5/${currentRegiao.id}/ineficientes`)
    ])
    
    if (!respSemaforos.ok) {
      console.error("Erro ao carregar semáforos:", respSemaforos.status, respSemaforos.statusText)
    }
    if (!respPostes.ok) {
      console.error("Erro ao carregar postes:", respPostes.status, respPostes.statusText)
    }
    
    let semaforos = []
    let postes = []
    
    if (respSemaforos.ok) {
      semaforos = await respSemaforos.json()
    }
    if (respPostes.ok) {
      postes = await respPostes.json()
    }
    
    document.getElementById("region-selected").innerHTML = `<h2>📍 ${currentRegiao.nome}</h2><p>${currentRegiao.descricao || ''}</p>`
    document.getElementById("dashboard-content").style.display = "block"
    
    document.getElementById("total-semaforos").innerText = semaforos.length
    document.getElementById("total-postes").innerText = postes.length
    
    const eficienciaSemaforos = semaforos.length > 0 
      ? (semaforos.reduce((sum, s) => sum + (s.eficiencia || 0), 0) / semaforos.length).toFixed(1)
      : 0
    const eficienciaPostes = postes.length > 0
      ? (postes.reduce((sum, p) => sum + (p.eficiencia || 0), 0) / postes.length).toFixed(1)
      : 0
    
    document.getElementById("eficiencia-semaforos").innerText = eficienciaSemaforos + "%"
    document.getElementById("eficiencia-postes").innerText = eficienciaPostes + "%"
    
    if (respTop5SemaforosEficientes.ok) {
      const semaforosEficientes = await respTop5SemaforosEficientes.json()
      const listHTML = semaforosEficientes.map((s, idx) => `
        <div class="top-item" onclick="mostrarDetalheSemaforo(${s.id})">
          <span class="rank">#${idx + 1}</span>
          <strong>${s.localizacao}</strong>
          <span class="efficiency">${s.eficiencia}%</span>
        </div>
      `).join("")
      document.getElementById('top-semaforos-eficientes').innerHTML = listHTML || "<p>Sem dados</p>"
    }
    
    if (respTop5SemaforosIneficientes.ok) {
      const semaforosIneficientes = await respTop5SemaforosIneficientes.json()
      const listHTML = semaforosIneficientes.map((s, idx) => `
        <div class="top-item" onclick="mostrarDetalheSemaforo(${s.id})">
          <span class="rank">#${idx + 1}</span>
          <strong>${s.localizacao}</strong>
          <span class="efficiency">${s.eficiencia}%</span>
        </div>
      `).join("")
      document.getElementById('top-semaforos-ineficientes').innerHTML = listHTML || "<p>Sem dados</p>"
    }
    
    if (respTop5PostesEficientes.ok) {
      const postesEficientes = await respTop5PostesEficientes.json()
      const listHTML = postesEficientes.map((p, idx) => `
        <div class="top-item" onclick="mostrarDetalhePoste(${p.id})">
          <span class="rank">#${idx + 1}</span>
          <strong>${p.localizacao}</strong>
          <span class="efficiency">${p.eficiencia}%</span>
        </div>
      `).join("")
      document.getElementById('top-postes-eficientes').innerHTML = listHTML || "<p>Sem dados</p>"
    }
    
    if (respTop5PostesIneficientes.ok) {
      const postesIneficientes = await respTop5PostesIneficientes.json()
      const listHTML = postesIneficientes.map((p, idx) => `
        <div class="top-item" onclick="mostrarDetalhePoste(${p.id})">
          <span class="rank">#${idx + 1}</span>
          <strong>${p.localizacao}</strong>
          <span class="efficiency">${p.eficiencia}%</span>
        </div>
      `).join("")
      document.getElementById('top-postes-ineficientes').innerHTML = listHTML || "<p>Sem dados</p>"
    }
    
    carregarSemaforos()
    carregarPostes()
  } catch (e) {
    console.error("Erro ao atualizar dashboard:", e)
    alert("❌ Erro ao atualizar dashboard: " + e.message)
  }
}

async function mostrarDetalheSemaforo(id) {
  try {
    const resp = await fetch(`/get_semaforo/${id}`)
    const semaforo = await resp.json()
    
    const getEstadoColor = (eficiencia) => eficiencia >= 80 ? '#2ecc71' : eficiencia >= 60 ? '#f39c12' : '#e74c3c'
    
    const html = `
      <h2>🚦 ${semaforo.localizacao}</h2>
      <div class="detail-grid">
        <div class="detail-item">
          <span class="label">ID:</span>
          <span class="value">${semaforo.id}</span>
        </div>
        <div class="detail-item">
          <span class="label">Estado:</span>
          <span class="value">${semaforo.estado}</span>
        </div>
        <div class="detail-item">
          <span class="label">Tempo de Ciclo:</span>
          <span class="value">${semaforo.tempo}s</span>
        </div>
        <div class="detail-item">
          <span class="label">Eficiência Geral:</span>
          <span class="value" style="color: ${getEstadoColor(semaforo.eficiencia)}; font-weight: bold; font-size: 1.2em;">${semaforo.eficiencia}%</span>
        </div>
      </div>
      
      <div style="margin-top: 15px; padding: 12px; background: #f8f9fa; border-left: 4px solid #3498db; border-radius: 5px;">
        <h4 style="margin: 0 0 12px 0; color: #2c3e50; font-size: 1em;">📊 Métricas de Eficiência (Padrões Reais):</h4>
        <div class="detail-grid" style="font-size: 0.85em;">
          <div class="detail-item" style="border: 1px solid #ecf0f1; padding: 8px; border-radius: 4px;">
            <span class="label">Fluxo de Veículos:</span>
            <span class="value" style="font-weight: bold;">${semaforo.fluxo_veiculos || 0} veic/min</span>
          </div>
          <div class="detail-item" style="border: 1px solid #ecf0f1; padding: 8px; border-radius: 4px;">
            <span class="label">Taxa de Ocupação:</span>
            <span class="value" style="font-weight: bold;">${semaforo.taxa_ocupacao || 0}%</span>
          </div>
          <div class="detail-item" style="border: 1px solid #ecf0f1; padding: 8px; border-radius: 4px;">
            <span class="label">Atraso Médio:</span>
            <span class="value" style="font-weight: bold;">${semaforo.atraso_medio || 0}s</span>
          </div>
          <div class="detail-item" style="border: 1px solid #ecf0f1; padding: 8px; border-radius: 4px;">
            <span class="label">Throughput:</span>
            <span class="value" style="font-weight: bold;">${semaforo.throughput || 0} veic/h</span>
          </div>
          <div class="detail-item" style="border: 1px solid #ecf0f1; padding: 8px; border-radius: 4px;">
            <span class="label">Comprimento de Fila:</span>
            <span class="value" style="font-weight: bold;">${semaforo.queue_length || 0}m</span>
          </div>
          <div class="detail-item" style="border: 1px solid #ecf0f1; padding: 8px; border-radius: 4px;">
            <span class="label">Estado Atual:</span>
            <span class="value" style="font-weight: bold; text-transform: uppercase;">${semaforo.estado}</span>
          </div>
        </div>
      </div>
      
      <div style="margin-top: 12px; font-size: 0.8em; color: #7f8c8d;">
        <p style="margin: 5px 0;"><strong>📌 Padrões de Referência:</strong></p>
        <ul style="margin: 5px 0; padding-left: 20px;">
          <li>Tempo Ótimo: 60-90s (MUTCD)</li>
          <li>Taxa Ocupação Ideal: 85-95%</li>
          <li>Atraso Aceitável: &lt;25s (HCM)</li>
          <li>Uniformidade de Fila: &lt;20m</li>
        </ul>
      </div>
      
      <div style="margin-top: 15px; display: flex; gap: 10px;">
        <button onclick="editarSemaforoFromModal(${semaforo.id})" class="btn-edit" style="flex: 1;">✏️ Editar</button>
        <button onclick="closeDetailModal()" class="btn-delete" style="flex: 1;">Fechar</button>
      </div>
    `
    
    document.getElementById("detail-content").innerHTML = html
    document.getElementById("detail-modal").style.display = "block"
  } catch (e) {
    console.error("Erro:", e)
  }
}

async function mostrarDetalhePoste(id) {
  try {
    const resp = await fetch(`/get_poste/${id}`)
    const poste = await resp.json()
    
    const getEstadoColor = (eficiencia) => eficiencia >= 80 ? '#2ecc71' : eficiencia >= 60 ? '#f39c12' : '#e74c3c'
    
    const html = `
      <h2>💡 ${poste.localizacao}</h2>
      <div class="detail-grid">
        <div class="detail-item">
          <span class="label">ID:</span>
          <span class="value">${poste.id}</span>
        </div>
        <div class="detail-item">
          <span class="label">Estado:</span>
          <span class="value">${poste.estado ? 'Ligado' : 'Desligado'}</span>
        </div>
        <div class="detail-item">
          <span class="label">Modo Automático:</span>
          <span class="value">${poste.atomatico ? 'Ativo' : 'Inativo'}</span>
        </div>
        <div class="detail-item">
          <span class="label">Eficiência Geral:</span>
          <span class="value" style="color: ${getEstadoColor(poste.eficiencia)}; font-weight: bold; font-size: 1.2em;">${poste.eficiencia}%</span>
        </div>
      </div>
      
      <div style="margin-top: 15px; padding: 12px; background: #f8f9fa; border-left: 4px solid #9b59b6; border-radius: 5px;">
        <h4 style="margin: 0 0 12px 0; color: #2c3e50; font-size: 1em;">💾 Parâmetros Luminotécnicos:</h4>
        <div class="detail-grid" style="font-size: 0.85em;">
          <div class="detail-item" style="border: 1px solid #ecf0f1; padding: 8px; border-radius: 4px;">
            <span class="label">Luminância Média:</span>
            <span class="value" style="font-weight: bold;">${(poste.luminancia_media || 0).toFixed(2)} cd/m²</span>
          </div>
          <div class="detail-item" style="border: 1px solid #ecf0f1; padding: 8px; border-radius: 4px;">
            <span class="label">Iluminância Média:</span>
            <span class="value" style="font-weight: bold;">${(poste.iluminancia_media || 0).toFixed(1)} lux</span>
          </div>
          <div class="detail-item" style="border: 1px solid #ecf0f1; padding: 8px; border-radius: 4px;">
            <span class="label">Iluminância Mínima:</span>
            <span class="value" style="font-weight: bold;">${(poste.iluminancia_minima || 0).toFixed(1)} lux</span>
          </div>
          <div class="detail-item" style="border: 1px solid #ecf0f1; padding: 8px; border-radius: 4px;">
            <span class="label">Uniformidade (min/média):</span>
            <span class="value" style="font-weight: bold;">${(poste.uniformidade || 0).toFixed(2)}</span>
          </div>
          <div class="detail-item" style="border: 1px solid #ecf0f1; padding: 8px; border-radius: 4px;">
            <span class="label">Consumo Real:</span>
            <span class="value" style="font-weight: bold;">${(poste.consumo_real || 0).toFixed(1)}W</span>
          </div>
          <div class="detail-item" style="border: 1px solid #ecf0f1; padding: 8px; border-radius: 4px;">
            <span class="label">Fator de Potência:</span>
            <span class="value" style="font-weight: bold;">${(poste.fator_potencia || 0).toFixed(3)}</span>
          </div>
        </div>
      </div>
      
      <div style="margin-top: 12px; font-size: 0.8em; color: #7f8c8d;">
        <p style="margin: 5px 0;"><strong>📌 Padrões de Referência (CIE/NBR/IEC):</strong></p>
        <ul style="margin: 5px 0; padding-left: 20px;">
          <li>Iluminância: 10-20 lux (vias urbanas)</li>
          <li>Luminância: 0.75-1.5 cd/m²</li>
          <li>Uniformidade: &gt;0.35</li>
          <li>Fator de Potência: &gt;0.95</li>
          <li>CRI: &gt;70 (reprodução de cor)</li>
        </ul>
      </div>
      
      <div style="margin-top: 15px; display: flex; gap: 10px;">
        <button onclick="editarPosteFromModal(${poste.id})" class="btn-edit" style="flex: 1;">✏️ Editar</button>
        <button onclick="closeDetailModal()" class="btn-delete" style="flex: 1;">Fechar</button>
      </div>
    `
    
    document.getElementById("detail-content").innerHTML = html
    document.getElementById("detail-modal").style.display = "block"
  } catch (e) {
    console.error("Erro:", e)
  }
}
    document.getElementById("detail-modal").style.display = "block"
  } catch (e) {
    console.error("Erro:", e)
  }
}

async function adicionarSemaforo() {
  if (!currentRegiao) {
    alert("⚠️ Selecione uma região primeiro")
    return
  }
  
  const localizacao = document.getElementById("semaforoLocalizacao").value.trim()
  const tempo = document.getElementById("semaforoTempo").value.trim()
  
  if (!localizacao || !tempo) {
    alert("⚠️ Preencha todos os campos")
    return
  }
  
  try {
    let resp
    if (currentEditSemaforoId) {
      resp = await fetch(`/update_semaforo/${currentEditSemaforoId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          localizacao, 
          estado: "verde",
          tempo: parseInt(tempo) 
        }),
      })
    } else {
      resp = await fetch("/add_semaforo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          regiao_id: currentRegiao.id,
          localizacao, 
          estado: "verde",
          tempo: parseInt(tempo) 
        }),
      })
    }
    
    if (resp.ok) {
      alert(currentEditSemaforoId ? "✅ Semáforo atualizado com sucesso!" : "✅ Semáforo adicionado com sucesso!")
      document.getElementById("semaforoLocalizacao").value = ""
      document.getElementById("semaforoTempo").value = ""
      currentEditSemaforoId = null
      carregarSemaforos()
      atualizarDashboard()
    } else {
      alert("❌ Erro ao salvar semáforo")
    }
  } catch (e) {
    console.error("Erro:", e)
    alert("❌ Erro na comunicação")
  }
}

async function carregarSemaforos() {
  if (!currentRegiao) {
    document.getElementById("semaforos-list").innerHTML = "<p class='loading'>Selecione uma região</p>"
    return
  }
  
  try {
    const resp = await fetch(`/semaforos?regiao_id=${currentRegiao.id}`)
    const semaforos = await resp.json()
    
    const listHTML = semaforos.map(s => `
      <div class="list-item" onclick="mostrarDetalheSemaforo(${s.id})">
        <div class="item-info">
          <strong>📍 ${s.localizacao}</strong>
          <p>ID: ${s.id} | Estado: ${s.estado} | Ciclo: ${s.tempo}s | Eficiência: ${s.eficiencia}%</p>
        </div>
        <div style="display: flex; gap: 5px;">
          <button onclick="event.stopPropagation(); editarSemaforo(${s.id})" class="btn-edit">✏️</button>
          <button onclick="event.stopPropagation(); deletarSemaforo(${s.id})" class="btn-delete">🗑️</button>
        </div>
      </div>
    `).join("")
    
    document.getElementById("semaforos-list").innerHTML = listHTML || "<p>Nenhum semáforo cadastrado</p>"
  } catch (e) {
    console.error("Erro ao carregar semáforos:", e)
    document.getElementById("semaforos-list").innerHTML = "<p class='error'>Erro ao carregar semáforos</p>"
  }
}

async function deletarSemaforo(id) {
  if (!confirm("Tem certeza que deseja deletar este semáforo?")) return
  
  try {
    await fetch(`/semaforos/${id}`, { method: "DELETE" })
    carregarSemaforos()
    atualizarDashboard()
  } catch (e) {
    console.error("Erro:", e)
  }
}

async function editarSemaforo(id) {
  try {
    const resp = await fetch(`/get_semaforo/${id}`)
    const semaforo = await resp.json()
    
    currentEditSemaforoId = id
    document.getElementById("semaforoLocalizacao").value = semaforo.localizacao
    document.getElementById("semaforoTempo").value = semaforo.tempo
    document.getElementById("semaforoLocalizacao").focus()
    closeDetailModal()
  } catch (e) {
    console.error("Erro:", e)
  }
}

async function editarSemaforoFromModal(id) {
  editarSemaforo(id)
}

async function adicionarPoste() {
  if (!currentRegiao) {
    alert("⚠️ Selecione uma região primeiro")
    return
  }
  
  const localizacao = document.getElementById("posteLocalizacao").value.trim()
  const automatico = document.getElementById("posteAutomatico").checked ? 1 : 0
  
  if (!localizacao) {
    alert("⚠️ Preencha a localização")
    return
  }
  
  try {
    let resp
    if (currentEditPosteId) {
      resp = await fetch(`/update_poste/${currentEditPosteId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          localizacao, 
          estado: 1,
          atomatico: automatico 
        }),
      })
    } else {
      resp = await fetch("/add_poste", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          regiao_id: currentRegiao.id,
          localizacao, 
          estado: 1,
          atomatico: automatico 
        }),
      })
    }
    
    if (resp.ok) {
      alert(currentEditPosteId ? "✅ Poste atualizado com sucesso!" : "✅ Poste adicionado com sucesso!")
      document.getElementById("posteLocalizacao").value = ""
      document.getElementById("posteAutomatico").checked = false
      currentEditPosteId = null
      carregarPostes()
      atualizarDashboard()
    } else {
      alert("❌ Erro ao salvar poste")
    }
  } catch (e) {
    console.error("Erro:", e)
    alert("❌ Erro na comunicação")
  }
}

async function carregarPostes() {
  if (!currentRegiao) {
    document.getElementById("postes-list").innerHTML = "<p class='loading'>Selecione uma região</p>"
    return
  }
  
  try {
    const resp = await fetch(`/postes?regiao_id=${currentRegiao.id}`)
    const postes = await resp.json()
    
    const listHTML = postes.map(p => `
      <div class="list-item" onclick="mostrarDetalhePoste(${p.id})">
        <div class="item-info">
          <strong>📍 ${p.localizacao}</strong>
          <p>ID: ${p.id} | Estado: ${p.estado ? "Ligado" : "Desligado"} | Automático: ${p.atomatico ? "Sim" : "Não"} | Eficiência: ${p.eficiencia}%</p>
        </div>
        <div style="display: flex; gap: 5px;">
          <button onclick="event.stopPropagation(); editarPoste(${p.id})" class="btn-edit">✏️</button>
          <button onclick="event.stopPropagation(); deletarPoste(${p.id})" class="btn-delete">🗑️</button>
        </div>
      </div>
    `).join("")
    
    document.getElementById("postes-list").innerHTML = listHTML || "<p>Nenhum poste cadastrado</p>"
  } catch (e) {
    console.error("Erro ao carregar postes:", e)
    document.getElementById("postes-list").innerHTML = "<p class='error'>Erro ao carregar postes</p>"
  }
}

async function deletarPoste(id) {
  if (!confirm("Tem certeza que deseja deletar este poste?")) return
  
  try {
    await fetch(`/postes/${id}`, { method: "DELETE" })
    carregarPostes()
    atualizarDashboard()
  } catch (e) {
    console.error("Erro:", e)
  }
}

async function editarPoste(id) {
  try {
    const resp = await fetch(`/get_poste/${id}`)
    const poste = await resp.json()
    
    currentEditPosteId = id
    document.getElementById("posteLocalizacao").value = poste.localizacao
    document.getElementById("posteAutomatico").checked = poste.atomatico ? true : false
    document.getElementById("posteLocalizacao").focus()
    closeDetailModal()
  } catch (e) {
    console.error("Erro:", e)
  }
}

async function editarPosteFromModal(id) {
  editarPoste(id)
}

function inicializar() {
  initializeMockData()
}

async function initializeMockData() {
  try {
    console.log("Iniciando verificação/criação de dados mock...")
    const resp = await fetch("/regioes")
    console.log("Resposta /regioes:", resp.status)
    
    if (!resp.ok) {
      if (resp.status === 401 || resp.status === 302) {
        console.log("Não autenticado em initializeMockData")
        window.location.href = "/logout"
        return
      }
      throw new Error(`HTTP ${resp.status}`)
    }
    
    const contentType = resp.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      console.error("Resposta não é JSON, content-type:", contentType)
      window.location.href = "/logout"
      return
    }
    
    const regioes = await resp.json()
    console.log("Regiões obtidas:", regioes.length, "itens")
    
    if (regioes.length === 0) {
      console.log("Sem regiões, criando dados mock...")
      const regioes_data = [
        { nome: "Centro da Cidade", descricao: "Região central com alta movimentação" },
        { nome: "Vila Mariana", descricao: "Região sul, área residencial e comercial" },
        { nome: "Pinheiros", descricao: "Região oeste, zona de negócios e finanças" }
      ]
      
      for (const regiao of regioes_data) {
        console.log("Criando região:", regiao.nome)
        const respAdd = await fetch("/add_regiao", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(regiao),
        })
        if (!respAdd.ok) {
          console.error("Erro ao criar região:", respAdd.status)
        }
      }
      
      const respRegioes = await fetch("/regioes")
      if (!respRegioes.ok) {
        console.error("Erro ao recarregar regiões:", respRegioes.status)
        throw new Error("Não conseguiu recarregar regiões após criação")
      }
      
      const regioesCriadas = await respRegioes.json()
      console.log("Regiões criadas:", regioesCriadas.length)
      
      for (const regiao of regioesCriadas) {
        let mockSemaforos = []
        let mockPostes = []
        
        if (regiao.nome === "Centro da Cidade") {
          mockSemaforos = [
            { regiao_id: regiao.id, localizacao: `Av. Paulista x Rua Augusta`, estado: "verde", tempo: 60 },
            { regiao_id: regiao.id, localizacao: `Rua 25 de Março x Rua São Bento`, estado: "vermelho", tempo: 45 },
            { regiao_id: regiao.id, localizacao: `Av. Rio Branco x Rua Tatuapé`, estado: "amarelo", tempo: 55 },
            { regiao_id: regiao.id, localizacao: `Av. Consolação x Av. Paulista`, estado: "verde", tempo: 50 },
            { regiao_id: regiao.id, localizacao: `Rua Barão de Itapetininga x Rua Augusta`, estado: "verde", tempo: 65 },
            { regiao_id: regiao.id, localizacao: `Largo do Arouche x Rua Rego Freitas`, estado: "amarelo", tempo: 48 },
            { regiao_id: regiao.id, localizacao: `Av. São João x Rua 24 de Maio`, estado: "verde", tempo: 70 },
            { regiao_id: regiao.id, localizacao: `Pça. da República x Rua General Osório`, estado: "vermelho", tempo: 60 }
          ]
          mockPostes = [
            { regiao_id: regiao.id, localizacao: `Av. Paulista, nº 1000`, estado: 1, atomatico: 1 },
            { regiao_id: regiao.id, localizacao: `Rua 25 de Março, nº 500`, estado: 1, atomatico: 0 },
            { regiao_id: regiao.id, localizacao: `Av. Consolação, nº 2000`, estado: 1, atomatico: 1 },
            { regiao_id: regiao.id, localizacao: `Largo do Arouche, nº 100`, estado: 0, atomatico: 1 },
            { regiao_id: regiao.id, localizacao: `Rua Barão de Itapetininga, nº 250`, estado: 1, atomatico: 0 },
            { regiao_id: regiao.id, localizacao: `Av. São João, nº 1200`, estado: 1, atomatico: 1 }
          ]
        } else if (regiao.nome === "Vila Mariana") {
          mockSemaforos = [
            { regiao_id: regiao.id, localizacao: `Av. Santo Amaro x Rua Bandeira`, estado: "verde", tempo: 55 },
            { regiao_id: regiao.id, localizacao: `Rua Vergueiro x Rua Dr. Bacelar`, estado: "amarelo", tempo: 50 },
            { regiao_id: regiao.id, localizacao: `Av. Domingos de Morais x Rua Abílio Soares`, estado: "verde", tempo: 60 },
            { regiao_id: regiao.id, localizacao: `Rua Pedroso x Rua Pio IV`, estado: "vermelho", tempo: 48 },
            { regiao_id: regiao.id, localizacao: `Av. Imigrantes x Rua Dr. Antenor Duarte`, estado: "verde", tempo: 65 },
            { regiao_id: regiao.id, localizacao: `Rua Apinajés x Rua Pedroso`, estado: "verde", tempo: 52 },
            { regiao_id: regiao.id, localizacao: `Av. Europa x Rua Tourinho`, estado: "amarelo", tempo: 58 },
            { regiao_id: regiao.id, localizacao: `Rua Marquês de São Vicente x Rua Jorge Americano`, estado: "verde", tempo: 62 }
          ]
          mockPostes = [
            { regiao_id: regiao.id, localizacao: `Av. Santo Amaro, nº 3000`, estado: 1, atomatico: 1 },
            { regiao_id: regiao.id, localizacao: `Rua Vergueiro, nº 1500`, estado: 1, atomatico: 1 },
            { regiao_id: regiao.id, localizacao: `Av. Domingos de Morais, nº 2500`, estado: 0, atomatico: 0 },
            { regiao_id: regiao.id, localizacao: `Rua Pedroso, nº 800`, estado: 1, atomatico: 0 },
            { regiao_id: regiao.id, localizacao: `Av. Imigrantes, nº 4000`, estado: 1, atomatico: 1 },
            { regiao_id: regiao.id, localizacao: `Rua Apinajés, nº 600`, estado: 1, atomatico: 1 }
          ]
        } else if (regiao.nome === "Pinheiros") {
          mockSemaforos = [
            { regiao_id: regiao.id, localizacao: `Av. Faria Lima x Rua Iracema`, estado: "verde", tempo: 65 },
            { regiao_id: regiao.id, localizacao: `Rua Bandeira x Rua Bom Jesus`, estado: "verde", tempo: 58 },
            { regiao_id: regiao.id, localizacao: `Av. Pedroso de Morais x Rua Funchal`, estado: "amarelo", tempo: 52 },
            { regiao_id: regiao.id, localizacao: `Rua Doutor Mário Ferraz x Av. Faria Lima`, estado: "vermelho", tempo: 50 },
            { regiao_id: regiao.id, localizacao: `Av. Rebouças x Rua Funcionários`, estado: "verde", tempo: 60 },
            { regiao_id: regiao.id, localizacao: `Rua da Consolação x Rua Dr. Elias Zarzur`, estado: "verde", tempo: 55 },
            { regiao_id: regiao.id, localizacao: `Av. Higienópolis x Rua Agostinho Rodrigues`, estado: "amarelo", tempo: 48 },
            { regiao_id: regiao.id, localizacao: `Rua Wisard x Av. Paulista`, estado: "verde", tempo: 70 }
          ]
          mockPostes = [
            { regiao_id: regiao.id, localizacao: `Av. Faria Lima, nº 2800`, estado: 1, atomatico: 1 },
            { regiao_id: regiao.id, localizacao: `Rua Bandeira, nº 1200`, estado: 1, atomatico: 1 },
            { regiao_id: regiao.id, localizacao: `Av. Pedroso de Morais, nº 1900`, estado: 1, atomatico: 0 },
            { regiao_id: regiao.id, localizacao: `Rua Doutor Mário Ferraz, nº 1100`, estado: 1, atomatico: 1 },
            { regiao_id: regiao.id, localizacao: `Av. Rebouças, nº 2100`, estado: 0, atomatico: 0 },
            { regiao_id: regiao.id, localizacao: `Rua Funcionários, nº 900`, estado: 1, atomatico: 1 }
          ]
        }
        
        console.log(`Criando ${mockSemaforos.length} semáforos e ${mockPostes.length} postes para ${regiao.nome}`)
        for (const semaforo of mockSemaforos) {
          await fetch("/add_semaforo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(semaforo),
          })
        }
        
        for (const poste of mockPostes) {
          await fetch("/add_poste", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(poste),
          })
        }
      }
      
      mockDataInitialized = true
      console.log("Dados mock criados com sucesso")
    } else {
      console.log("Regiões já existem, pulando criação de mock")
    }
    
    console.log("Chamando carregarRegioes...")
    carregarRegioes()
  } catch (e) {
    console.error("Erro ao inicializar dados mock:", e)
    if (document.getElementById("regioes-list")) {
      console.log("Carregando regiões apesar do erro")
      carregarRegioes()
    }
  }
}

setInterval(() => {
  if (currentRegiao) {
    atualizarDashboard()
  }
}, 5000)

async function verificarAutenticacao() {
  try {
    console.log("Verificando autenticação...")
    const resp = await fetch("/api/auth-status")
    console.log("Status de autenticação:", resp.status)
    
    if (resp.status === 401) {
      console.log("Não autenticado, redirecionando para login")
      window.location.href = "/"
      return false
    }
    
    if (!resp.ok) {
      console.log("Erro ao verificar autenticação:", resp.status)
      window.location.href = "/"
      return false
    }
    
    const data = await resp.json()
    console.log("Usuário autenticado:", data.usuario)
    return true
  } catch (e) {
    console.error("Erro ao verificar autenticação:", e)
    window.location.href = "/"
    return false
  }
}

// ========== INICIALIZAÇÃO SIMPLES ==========

console.log("[INIT] Iniciando carregamento de regiões...")

async function carregarRegioes() {
  try {
    const resp = await fetch("/regioes")
    if (!resp.ok) {
      console.error("[REGIOES] Erro:", resp.status)
      document.getElementById("regioes-list").innerHTML = "<p>Erro ao carregar</p>"
      return
    }
    
    const regioes = await resp.json()
    console.log("[REGIOES] Carregadas:", regioes.length)
    regioesList = regioes
    
    const html = regioes.map(r => `
      <div class="regiao-item" onclick="selecionarRegiao(${r.id}, event)">
        <strong>${r.nome}</strong>
        ${r.descricao ? `<p>${r.descricao}</p>` : ''}
      </div>
    `).join("")
    
    document.getElementById("regioes-list").innerHTML = html
  } catch (e) {
    console.error("[REGIOES] Erro:", e)
  }
}

function inicializar() {
  console.log("[INIT] Iniciando sistema...")
  carregarRegioes()
}

// Executar imediatamente
console.log("[INIT] DOM state:", document.readyState)
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", inicializar)
} else {
  setTimeout(inicializar, 100)
}

console.log("[INIT] Script finalizado")

