const cicloDiaNoite = {
  estados: ["amanhecer", "dia", "entardecer", "noite"],
  indiceAtual: 0,
  estadoAtual: "amanhecer",
}

function toggleForms(event) {
  event.preventDefault()
  const loginForm = document.getElementById("login-form")
  const registerForm = document.getElementById("register-form")
  const message = document.getElementById("message")

  loginForm.classList.toggle("active")
  registerForm.classList.toggle("active")
  message.style.display = "none"
}

function showMessage(text, type) {
  const message = document.getElementById("message")
  message.textContent = text
  message.className = `message ${type}`
  message.style.display = "block"
}

async function handleLogin(event) {
  event.preventDefault()

  const usuario = document.getElementById("login-usuario").value
  const senha = document.getElementById("login-senha").value

  try {
    const response = await fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ usuario, senha }),
    })

    const data = await response.json()

    if (response.ok) {
      showMessage("✅ Login realizado com sucesso! Redirecionando...", "success")
      setTimeout(() => {
        window.location.href = "/dashboard"
      }, 1000)
    } else {
      showMessage(data.erro || "❌ Erro ao fazer login", "error")
    }
  } catch (error) {
    showMessage("❌ Erro ao conectar com o servidor", "error")
    console.error("Erro:", error)
  }
}

async function handleRegister(event) {
  event.preventDefault()

  const usuario = document.getElementById("register-usuario").value
  const senha = document.getElementById("register-senha").value
  const senhaConfirm = document.getElementById("register-senha-confirm").value

  if (senha !== senhaConfirm) {
    showMessage("❌ As senhas não coincidem", "error")
    return
  }

  if (senha.length < 6) {
    showMessage("❌ A senha deve ter pelo menos 6 caracteres", "error")
    return
  }

  try {
    const response = await fetch("/add_user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ usuario, senha }),
    })

    const data = await response.json()

    if (response.ok) {
      showMessage("✅ Usuário registrado com sucesso! Faça login.", "success")
      setTimeout(() => {
        document.getElementById("register-usuario").value = ""
        document.getElementById("register-senha").value = ""
        document.getElementById("register-senha-confirm").value = ""
        toggleForms(new Event("click"))
      }, 1500)
    } else {
      showMessage(data.erro || "❌ Erro ao registrar usuário", "error")
    }
  } catch (error) {
    showMessage("❌ Erro ao conectar com o servidor", "error")
    console.error("Erro:", error)
  }
}
