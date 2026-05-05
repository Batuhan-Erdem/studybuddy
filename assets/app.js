let tasks = JSON.parse(localStorage.getItem("tasks")) || [];

// 🔥 EKLENDİ
let currentPlan = null;

function saveCurrentPlan(plan) {
  localStorage.setItem("currentPlan", JSON.stringify(plan));
}

function loadCurrentPlan() {
  const saved = localStorage.getItem("currentPlan");
  return saved ? JSON.parse(saved) : null;
}

function showToast(title, message) {
  let container = document.querySelector(".toast-container");

  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = "toast";

  toast.innerHTML = `
    <div class="toast-title">${title}</div>
    <div class="toast-message">${message}</div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(-8px)";
    toast.style.transition = "0.25s ease";
    setTimeout(() => toast.remove(), 250);
  }, 2600);
}

function scrollToResult() {
  const el = document.getElementById("plannerResult");
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function saveTasks() {
  localStorage.setItem("tasks", JSON.stringify(tasks));
}

function renderTasks() {
  const list = document.getElementById("taskList");
  const searchInput = document.getElementById("searchInput");
  const filterSelect = document.getElementById("filterSelect");
  const counter = document.getElementById("taskCounter");

  if (!list) return;

  const searchText = (searchInput?.value || "").toLowerCase();
  const filterValue = filterSelect?.value || "all";

  let filtered = tasks.filter(t => t.text.toLowerCase().includes(searchText));

  if (filterValue === "active") filtered = filtered.filter(t => !t.done);
  if (filterValue === "done") filtered = filtered.filter(t => t.done);

  list.innerHTML = "";

  filtered.forEach((task) => {
    const realIndex = tasks.indexOf(task);

    const li = document.createElement("li");
    li.style.display = "flex";
    li.style.gap = "10px";
    li.style.alignItems = "center";
    li.style.justifyContent = "space-between";
    li.style.padding = "10px";
    li.style.border = "1px solid rgba(255,255,255,0.10)";
    li.style.borderRadius = "12px";
    li.style.marginBottom = "8px";
    li.style.background = "rgba(255,255,255,0.03)";

    li.style.background = task.done
      ? "rgba(66, 211, 146, 0.08)"
      : "rgba(255,255,255,0.03)";

    li.style.border = task.done
      ? "1px solid rgba(66, 211, 146, 0.22)"
      : "1px solid rgba(255,255,255,0.10)";

    li.innerHTML = `
  <span style="flex:1; ${task.done ? 'text-decoration:line-through; opacity:0.7;' : ''}">
    ${task.text}
  </span>
  <div style="display:flex; gap:8px; align-items:center;">
    ${task.done
        ? `<span class="task-done-badge">Tamamlandı</span>`
        : `<button class="task-mini-btn" onclick="toggleTask(${realIndex})">✔</button>`
      }
    <button class="task-mini-btn delete-btn" onclick="deleteTask(${realIndex})">❌</button>
  </div>
`;

    list.appendChild(li);
  });

  const doneCount = tasks.filter(t => t.done).length;
  if (counter) {
    counter.textContent = `${tasks.length} görev • ${doneCount} tamamlandı`;
  }
}

function addTask() {
  const input = document.getElementById("taskInput");
  if (!input) return;

  const text = input.value.trim();
  if (text === "") return;

  tasks.push({
    text: text,
    done: false
  });

  input.value = "";
  saveTasks();
  renderTasks();
}

function toggleTask(index) {
  tasks[index].done = !tasks[index].done;
  saveTasks();
  renderTasks();
}

function deleteTask(index) {
  tasks.splice(index, 1);
  saveTasks();
  renderTasks();
}

document.addEventListener("input", (e) => {
  if (e.target.id === "searchInput") renderTasks();
});

document.addEventListener("change", (e) => {
  if (e.target.id === "filterSelect") renderTasks();
});

renderTasks();

/* =========================
   AI STUDY PLANNER
========================= */

const API_BASE_URL = "http://127.0.0.1:8000";

const studyPlannerForm = document.getElementById("studyPlannerForm");
const pdfInput = document.getElementById("pdfInput");
const pdfAnalyzeBtn = document.getElementById("pdfAnalyzeBtn");
const pdfPlanBtn = document.getElementById("pdfPlanBtn");
const pdfDeadlineInput = document.getElementById("pdfDeadlineInput");
const pdfHoursInput = document.getElementById("pdfHoursInput");
const pdfAnalysisStatus = document.getElementById("pdfAnalysisStatus");
const goalInput = document.getElementById("goalInput");
const daysInput = document.getElementById("daysInput");
const hoursInput = document.getElementById("hoursInput");

const plannerLoading = document.getElementById("plannerLoading");
const plannerError = document.getElementById("plannerError");
const plannerEmptyState = document.getElementById("plannerEmptyState");
const plannerResult = document.getElementById("plannerResult");
const plannerStatusText = document.getElementById("plannerStatusText");

const planTitle = document.getElementById("planTitle");
const planDays = document.getElementById("planDays");
const planTips = document.getElementById("planTips");

const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatSendBtn = document.getElementById("chatSendBtn");
const chatMessages = document.getElementById("chatMessages");
const chatStatusText = document.getElementById("chatStatusText");

let selectedPdfFile = null;
let extractedPdfContent = "";

function setPlannerLoading(isLoading) {
  if (!plannerLoading) return;
  plannerLoading.classList.toggle("hidden", !isLoading);
  if (studyPlannerForm) {
    const submitButton = studyPlannerForm.querySelector('button[type="submit"]');
    if (submitButton) {
      submitButton.disabled = isLoading;
      submitButton.textContent = isLoading ? "Oluşturuluyor..." : "Plan Oluştur";
    }
  }
}

function showPlannerError(message) {
  if (!plannerError) return;
  plannerError.textContent = message;
  plannerError.classList.remove("hidden");
}

function clearPlannerError() {
  if (!plannerError) return;
  plannerError.textContent = "";
  plannerError.classList.add("hidden");
}

function setPdfStatus(message, variant = "info") {
  if (!pdfAnalysisStatus) return;
  pdfAnalysisStatus.textContent = message;
  pdfAnalysisStatus.className = "pdf-analysis-status";
  pdfAnalysisStatus.classList.add(variant);
}

function setPdfLoading(isLoading) {
  if (pdfAnalyzeBtn) {
    pdfAnalyzeBtn.disabled = isLoading;
    pdfAnalyzeBtn.textContent = isLoading ? "Analiz ediliyor..." : "PDF’i Analiz Et";
  }
}

function setPdfPlanLoading(isLoading) {
  if (pdfPlanBtn) {
    pdfPlanBtn.disabled = isLoading;
    pdfPlanBtn.textContent = isLoading ? "Plan oluşturuluyor..." : "PDF Kartından Plan Oluştur";
  }
}


async function handlePdfAnalyze() {
  if (!pdfInput || !pdfInput.files || !pdfInput.files[0]) {
    setPdfStatus("Önce bir PDF dosyası seçmelisin.", "warning");
    return;
  }
  selectedPdfFile = pdfInput.files[0];
  setPdfLoading(true);
  setPdfStatus("PDF analiz ediliyor (MCP)...", "info");
  try {
    const formData = new FormData();
    formData.append("file", selectedPdfFile);
    const response = await fetch(`${API_BASE_URL}/analyze-pdf`, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) throw new Error("PDF analiz edilemedi.");
    const data = await response.json();
    extractedPdfContent = data.content || "";
    setPdfStatus(`PDF başarıyla analiz edildi. ${data.page_count} sayfa içeriği okundu.`, "success");
  } catch (error) {
    setPdfStatus("PDF analiz edilemedi. Backend'i kontrol et.", "error");
    console.error(error);
  } finally {
    setPdfLoading(false);
  }
}

async function handlePdfPlan() {
  if (!selectedPdfFile && (!pdfInput || !pdfInput.files || !pdfInput.files[0])) {
    setPdfStatus("Önce bir PDF dosyası seçmelisin.", "warning");
    return;
  }
  if (!pdfDeadlineInput || !pdfDeadlineInput.value) {
    setPdfStatus("Deadline tarihini girmen gerekiyor.", "warning");
    return;
  }
  const hoursPerDay = Number(pdfHoursInput?.value);
  if (!hoursPerDay) {
    setPdfStatus("Günlük saat bilgisini girmen gerekiyor.", "warning");
    return;
  }

  // UI Hazırlığı
  clearPlannerError();
  setPdfPlanLoading(true);
  
  if (plannerResult) plannerResult.classList.add("hidden");
  if (plannerEmptyState) plannerEmptyState.classList.add("hidden");
  if (plannerStatusText) plannerStatusText.textContent = "Yapay zekâ planın hazırlanıyor...";
  setPlannerLoading(true);

  try {
    // Adım 1: Eğer henüz analiz edilmemişse analiz et (MCP)
    if (!extractedPdfContent) {
      setPdfStatus("Önce PDF içeriği analiz ediliyor...", "info");
      const formData = new FormData();
      formData.append("file", selectedPdfFile || pdfInput.files[0]);
      const analyzeRes = await fetch(`${API_BASE_URL}/analyze-pdf`, {
        method: "POST",
        body: formData,
      });
      if (!analyzeRes.ok) throw new Error("Otomatik analiz başarısız.");
      const analyzeData = await analyzeRes.json();
      extractedPdfContent = analyzeData.content || "";
    }

    // Adım 2: Saf JSON ile plan isteği gönder (Çalışan /plan-study ucunu kullanıyoruz)
    setPdfStatus("Plan oluşturuluyor (JSON)...", "info");
    
    // Hedefi PDF içeriğine göre kurgula
    const goal = `Bu PDF içeriğine göre bir çalışma planı hazırla. Deadline: ${pdfDeadlineInput.value}. İçerik: ${extractedPdfContent}`;
    
    // Tarihten gün farkını hesapla (Frontend tarafında da yapılabilir veya backend halleder)
    const deadlineDate = new Date(pdfDeadlineInput.value);
    const today = new Date();
    const daysDiff = Math.max(1, Math.ceil((deadlineDate - today) / (1000 * 60 * 60 * 24)));

    const response = await fetch(`${API_BASE_URL}/plan-study`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        goal: goal,
        days: daysDiff,
        hours_per_day: hoursPerDay
      }),
    });

    if (!response.ok) throw new Error("Plan oluşturulamadı.");
    const data = await response.json();
    renderPlannerResult(data);
    setPdfStatus("PDF içeriğine göre plan başarıyla oluşturuldu.", "success");
  } catch (error) {
    if (plannerEmptyState) plannerEmptyState.classList.remove("hidden");
    if (plannerStatusText) plannerStatusText.textContent = "Bir hata oluştu.";
    setPdfStatus("Plan oluşturulamadı. Lütfen tekrar dene.", "error");
    console.error(error);
  } finally {
    setPdfPlanLoading(false);
    setPlannerLoading(false);
  }
}



function renderPlannerResult(data) {
  if (!data || !data.plan) return;
  currentPlan = data.plan;
  saveCurrentPlan(currentPlan);
  if (plannerEmptyState) plannerEmptyState.classList.add("hidden");
  if (plannerResult) plannerResult.classList.remove("hidden");
  if (plannerStatusText) plannerStatusText.textContent = "Plan başarıyla oluşturuldu.";
  if (planTitle) planTitle.textContent = data.plan.title || "Oluşturulan Çalışma Planı";
  if (planDays) {
    planDays.innerHTML = "";
    (data.plan.days || []).forEach((dayItem) => {
      const card = document.createElement("div");
      card.className = "day-card";
      const tasksHtml = (dayItem.tasks || [])
        .map(task => `<li>${task}</li>`)
        .join("");
      card.innerHTML = `
        <div class="day-card-top">
          <span class="day-badge">Gün ${dayItem.day}</span>
          <span class="day-duration">${dayItem.duration_hours} saat</span>
        </div>
        <h4>${dayItem.focus}</h4>
        <ul class="day-task-list">
          ${tasksHtml}
        </ul>
        <button class="add-day-btn" onclick="addDayToTasks(${dayItem.day})">
          ➕ Günü Görevlere Ekle
        </button>
      `;
      planDays.appendChild(card);
    });
  }
  if (planTips) {
    planTips.innerHTML = "";
    (data.plan.tips || []).forEach((tip) => {
      const li = document.createElement("li");
      li.textContent = tip;
      planTips.appendChild(li);
    });
  }
  scrollToResult();
}

function addDayToTasks(dayNumber) {
  if (!currentPlan) return;
  const day = currentPlan.days.find(d => d.day === dayNumber);
  if (!day) return;
  day.tasks.forEach(taskText => {
    tasks.push({ text: taskText, done: false });
  });
  saveTasks();
  renderTasks();
  showToast("Görevler eklendi", `Gün ${dayNumber} içindeki ${day.tasks.length} görev listene eklendi.`);
}

async function handleStudyPlannerSubmit(event) {
  event.preventDefault();
  if (!goalInput || !daysInput || !hoursInput) return;
  const goal = goalInput.value.trim();
  const days = Number(daysInput.value);
  const hours_per_day = Number(hoursInput.value);
  if (!goal || !days || !hours_per_day) {
    showPlannerError("Lütfen tüm alanları doldur.");
    return;
  }
  clearPlannerError();
  setPlannerLoading(true);
  if (plannerResult) plannerResult.classList.add("hidden");
  if (plannerEmptyState) plannerEmptyState.classList.add("hidden");
  if (plannerStatusText) plannerStatusText.textContent = "Yapay zekâ planın hazırlanıyor...";
  try {
    const response = await fetch(`${API_BASE_URL}/plan-study`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal, days, hours_per_day })
    });
    if (!response.ok) throw new Error("Plan oluşturulamadı.");
    const data = await response.json();
    renderPlannerResult(data);
  } catch (error) {
    if (plannerEmptyState) plannerEmptyState.classList.remove("hidden");
    if (plannerStatusText) plannerStatusText.textContent = "Bir hata oluştu.";
    showPlannerError("⚠️ Yapay zekâ servisine bağlanılamadı. Backend çalışıyor mu kontrol et.");
    console.error(error);
  } finally {
    setPlannerLoading(false);
  }
}

/* =========================
   PLAN ASSISTANT CHAT
========================= */

function saveChatHistory(history) {
  localStorage.setItem("chatHistory", JSON.stringify(history));
}

function loadChatHistory() {
  const saved = localStorage.getItem("chatHistory");
  return saved ? JSON.parse(saved) : [];
}

let chatHistory = loadChatHistory();

function renderChatMessages() {
  if (!chatMessages) return;
  chatMessages.innerHTML = "";
  if (!chatHistory.length) {
    const empty = document.createElement("div");
    empty.className = "chat-bubble assistant";
    empty.textContent = "Merhaba! Planınla ilgili sorularını buradan sorabilirsin.";
    chatMessages.appendChild(empty);
    return;
  }
  chatHistory.forEach((m) => {
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${m.role}`;
    bubble.textContent = m.content;
    chatMessages.appendChild(bubble);
  });
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function handleChatSubmit(event) {
  event.preventDefault();
  if (!chatInput) return;
  const message = chatInput.value.trim();
  if (!message) return;
  chatInput.value = "";
  if (chatInput) chatInput.disabled = true;
  if (chatSendBtn) chatSendBtn.disabled = true;
  if (chatStatusText) chatStatusText.textContent = "Asistan düşünüyor...";
  chatHistory.push({ role: "user", content: message });
  saveChatHistory(chatHistory);
  renderChatMessages();
  try {
    const plan = loadCurrentPlan();
    const recentHistory = chatHistory.slice(-10);
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, plan, history: recentHistory }),
    });
    if (!response.ok) throw new Error("Chat yanıtı alınamadı.");
    const data = await response.json();
    const reply = (data && data.reply) ? String(data.reply) : "";
    chatHistory.push({ role: "assistant", content: reply || "Bir cevap üretemedim." });
    saveChatHistory(chatHistory);
    renderChatMessages();
    if (chatStatusText) chatStatusText.textContent = "Yanıt hazır.";
  } catch (error) {
    chatHistory.push({ role: "assistant", content: "⚠️ Asistana bağlanılamadı. Backend çalışıyor mu kontrol et." });
    saveChatHistory(chatHistory);
    renderChatMessages();
    if (chatStatusText) chatStatusText.textContent = "Bir hata oluştu.";
    console.error(error);
  } finally {
    if (chatInput) chatInput.disabled = false;
    if (chatSendBtn) chatSendBtn.disabled = false;
    if (chatInput) chatInput.focus();
  }
}

// Event Listeners Initialization
function initApp() {
  console.log("StudyBuddy: Initializing app...");
  if (studyPlannerForm) studyPlannerForm.addEventListener("submit", handleStudyPlannerSubmit);
  if (pdfAnalyzeBtn) pdfAnalyzeBtn.addEventListener("click", handlePdfAnalyze);
  if (pdfPlanBtn) pdfPlanBtn.addEventListener("click", handlePdfPlan);
  if (pdfInput) {
    pdfInput.addEventListener("change", () => {
      selectedPdfFile = pdfInput.files && pdfInput.files[0] ? pdfInput.files[0] : null;
      if (selectedPdfFile) {
        setPdfStatus("PDF seçildi. Analiz etmeye hazırsın.", "info");
      } else {
        if (pdfAnalysisStatus) {
          pdfAnalysisStatus.textContent = "";
          pdfAnalysisStatus.className = "pdf-analysis-status hidden";
        }
      }
    });
  }
  if (chatForm) {
    renderChatMessages();
    chatForm.addEventListener("submit", handleChatSubmit);
  }
  const savedPlan = loadCurrentPlan();
  if (savedPlan) renderPlannerResult({ plan: savedPlan });
}

document.addEventListener("DOMContentLoaded", initApp);