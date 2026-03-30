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
    ${
      task.done
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

function renderPlannerResult(data) {
  if (!data || !data.plan) return;

  // 🔥 EKLENDİ
  currentPlan = data.plan;
  saveCurrentPlan(currentPlan);

  if (plannerEmptyState) plannerEmptyState.classList.add("hidden");
  if (plannerResult) plannerResult.classList.remove("hidden");

  if (plannerStatusText) {
    plannerStatusText.textContent = "Plan başarıyla oluşturuldu.";
  }

  if (planTitle) {
    planTitle.textContent = data.plan.title || "Oluşturulan Çalışma Planı";
  }

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

// 🔥 TAM ÇALIŞAN HAL
function addDayToTasks(dayNumber) {
  if (!currentPlan) return;

  const day = currentPlan.days.find(d => d.day === dayNumber);
  if (!day) return;

  day.tasks.forEach(taskText => {
    tasks.push({
      text: taskText,
      done: false
    });
  });

  saveTasks();
  renderTasks();

  showToast(
    "Görevler eklendi",
    `Gün ${dayNumber} içindeki ${day.tasks.length} görev başarıyla listene eklendi.`
  );
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
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        goal,
        days,
        hours_per_day
      })
    });

    if (!response.ok) {
      throw new Error("Plan oluşturulamadı.");
    }

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

if (studyPlannerForm) {
  studyPlannerForm.addEventListener("submit", handleStudyPlannerSubmit);
}

const savedPlan = loadCurrentPlan();

if (savedPlan) {
  renderPlannerResult({ plan: savedPlan });
}