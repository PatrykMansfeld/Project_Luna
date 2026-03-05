const API = "http://127.0.0.1:8000";

const sessionId = localStorage.getItem("session_id") || (() => {
  const v = "sess_" + Math.random().toString(16).slice(2, 10);
  localStorage.setItem("session_id", v);
  return v;
})();

const chatEl = document.getElementById("chat");
const inp = document.getElementById("inp");
const sendBtn = document.getElementById("sendBtn");
const resetBtn = document.getElementById("resetBtn");
const ollamaEl = document.getElementById("ollama");
const botNameEl = document.getElementById("botName");
const themeToggle = document.getElementById("themeToggle");
const screenSelect = document.getElementById("screenSelect");
const screenChat = document.getElementById("screenChat");
const personaGrid = document.getElementById("personaGrid");
const changePersonaBtn = document.getElementById("changePersonaBtn");

// Defensive: if critical elements are missing, fail fast to avoid hard-to-debug null errors.
if (!chatEl || !inp || !sendBtn || !resetBtn || !ollamaEl || !botNameEl || !screenSelect || !screenChat || !personaGrid || !changePersonaBtn) {
  // eslint-disable-next-line no-console
  console.error("Brakuje wymaganych elementów DOM. Sprawdź index.html (id: chat, inp, sendBtn, resetBtn, ollama, botName, screenSelect, screenChat, personaGrid, changePersonaBtn).");
}

const THEME_KEY = "theme";
const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
const storedTheme = localStorage.getItem(THEME_KEY);
const initialTheme = storedTheme || (prefersDark ? "dark" : "light");

let personas = [];
let currentPersona = null;

function setTheme(theme) {
  document.body.dataset.theme = theme;
  if (themeToggle) {
    themeToggle.textContent = theme === "dark" ? "Tryb jasny" : "Tryb ciemny";
    themeToggle.setAttribute("aria-pressed", theme === "dark");
  }
  localStorage.setItem(THEME_KEY, theme);
}

function addMsg(text, who) {
  // Rysuje dymek wiadomości i przewija widok na dół.
  if (!chatEl) return;
  const d = document.createElement("div");
  d.className = "msg " + (who === "me" ? "me" : "bot");
  d.textContent = text;
  chatEl.appendChild(d);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function ollamaStatus() {
  // Sprawdza zdrowie backendu i pokazuje status w nagłówku.
  if (!ollamaEl) return;
  try {
    const r = await fetch(API + "/ollama");
    const data = await r.json();
    ollamaEl.textContent = `OK, model: ${data.model}`;
  } catch (e) {
    ollamaEl.textContent = "Brak połączenia z backendem";
  }
}

function showSelect() {
  if (!screenSelect || !screenChat) return;
  screenSelect.classList.remove("hidden");
  screenChat.classList.add("hidden");
}

function showChat() {
  if (!screenSelect || !screenChat) return;
  screenSelect.classList.add("hidden");
  screenChat.classList.remove("hidden");
  inp?.focus();
}

function greeting(name) {
  return `Hej, tu ${name}. O czym chcesz pogadac?`;
}

function selectPersona(persona) {
  currentPersona = persona;
  if (botNameEl) botNameEl.textContent = persona.name || "Bot";
  if (chatEl) chatEl.innerHTML = "";
  addMsg(greeting(botNameEl?.textContent || "Bot"), "bot");
  showChat();
}

function renderPersonas(list) {
  if (!personaGrid) return;
  personaGrid.innerHTML = "";
  if (!list.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "Brak person do wyboru.";
    personaGrid.appendChild(empty);
    return;
  }

  list.forEach((p) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "persona-card";

    const name = document.createElement("div");
    name.className = "persona-name";
    name.textContent = p.name || p.id;

    const blurb = document.createElement("div");
    blurb.className = "persona-blurb";
    blurb.textContent = p.blurb || "Rozpocznij rozmowe";

    const action = document.createElement("div");
    action.className = "persona-action";
    action.textContent = "Wybierz";

    card.appendChild(name);
    card.appendChild(blurb);
    card.appendChild(action);

    card.addEventListener("click", () => selectPersona(p));
    personaGrid.appendChild(card);
  });
}

async function loadPersonas() {
  try {
    const r = await fetch(API + "/personas");
    const data = await r.json();
    personas = data.personas || [];
    renderPersonas(personas);
  } catch (e) {
    renderPersonas([]);
  }
}

async function send() {
  // Wysyła bieżący tekst jako wiadomość i renderuje odpowiedź.
  if (!currentPersona) {
    showSelect();
    return;
  }

  const text = inp?.value?.trim?.() ?? "";
  if (!text) return;

  if (inp) inp.value = "";
  addMsg(text, "me");

  if (sendBtn) sendBtn.disabled = true;

  try {
    const r = await fetch(API + "/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        user_message: text,
        persona_id: currentPersona.id
      })
    });

    const data = await r.json();

    if (!r.ok) {
      addMsg("Coś poszło nie tak: " + (data.detail || "error"), "bot");
    } else {
      if (botNameEl) botNameEl.textContent = data.bot_name || "Bot";
      addMsg(data.reply, "bot");
    }
  } catch (e) {
    addMsg("Nie mogę się połączyć z backendem.", "bot");
  } finally {
    if (sendBtn) sendBtn.disabled = false;
    inp?.focus();
  }
}

async function reset() {
  // Resetuje stan rozmowy w backendzie i czyści historię w UI.
  if (!currentPersona) {
    showSelect();
    return;
  }
  try {
    await fetch(API + "/reset/" + sessionId, { method: "POST" });
  } catch (e) {
    // nawet jak reset na backendzie nie wyjdzie, czyścimy UI
  }
  if (chatEl) chatEl.innerHTML = "";
  addMsg(greeting(botNameEl?.textContent || "Bot"), "bot");
  inp?.focus();
}

// Bind events only if elements exist
sendBtn?.addEventListener("click", send);
inp?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") send();
});
resetBtn?.addEventListener("click", reset);
changePersonaBtn?.addEventListener("click", () => {
  currentPersona = null;
  if (chatEl) chatEl.innerHTML = "";
  showSelect();
});
if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const next = document.body.dataset.theme === "dark" ? "light" : "dark";
    setTheme(next);
  });
}

setTheme(initialTheme);
showSelect();
loadPersonas();
ollamaStatus();
