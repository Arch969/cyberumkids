// Простая структура уровней: координаты в процентах относительно контейнера (16:9)
const LEVELS = [
  { id: 1, title: "1. Привет, Скретч!",    x: 10, y: 75, lessonUrl: "/courses/scratch/lesson/1", desc: "Знакомство со сценой и спрайтами." },
  { id: 2, title: "2. Двигаемся и говорим", x: 24, y: 58, lessonUrl: "/courses/scratch/lesson/2", desc: "Команды движения и реплики." },
  { id: 3, title: "3. Циклы и события",     x: 40, y: 40, lessonUrl: "/courses/scratch/lesson/3", desc: "События, forever и repeat." },
  { id: 4, title: "4. Сцены и костюмы",     x: 62, y: 32, lessonUrl: "/courses/scratch/lesson/4", desc: "Фоны, костюмы, переключения." },
  { id: 5, title: "5. Первая мини-игра",    x: 82, y: 54, lessonUrl: "/courses/scratch/lesson/5", desc: "Собираем мини-игру из блоков." },
];

// Простая «сохранёнка»: какой уровень пройден и сколько открыто
const STORAGE_KEY = "scratch_map_progress"; // { current: number, unlocked: number }

const stageEl = document.getElementById("map-stage");
const catEl = document.getElementById("cat");
const hudCurrent = document.getElementById("hud-current");
const hudUnlocked = document.getElementById("hud-unlocked");
const hudTotal = document.getElementById("hud-total");
const resetBtn = document.getElementById("reset-progress");

// Модалка
const modal = document.getElementById("level-modal");
const modalClose = document.getElementById("modal-close");
const modalCancel = document.getElementById("modal-cancel");
const modalTitle = document.getElementById("modal-title");
const modalDesc = document.getElementById("modal-desc");
const modalStart = document.getElementById("modal-start");

hudTotal.textContent = LEVELS.length;

function getProgress() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || { current: 1, unlocked: 1 };
  } catch {
    return { current: 1, unlocked: 1 };
  }
}
function setProgress(p) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(p));
  updateHUD(p);
  updateDots(p);
}
function updateHUD(p) {
  hudCurrent.textContent = p.current;
  hudUnlocked.textContent = p.unlocked;
}

function createLevelDots() {
  LEVELS.forEach((lvl) => {
    const dot = document.createElement("button");
    dot.className = "level-dot";
    dot.style.left = `${lvl.x}%`;
    dot.style.top = `${lvl.y}%`;
    dot.setAttribute("data-level-id", lvl.id);
    dot.setAttribute("aria-label", `Уровень ${lvl.id}: ${lvl.title}`);
    dot.title = lvl.title;

    const badge = document.createElement("div");
    badge.className = "level-badge";
    badge.textContent = lvl.title;
    badge.style.left = `${lvl.x}%`;
    badge.style.top  = `${lvl.y}%`;

    dot.addEventListener("click", () => onLevelClick(lvl));
    stageEl.appendChild(dot);
    stageEl.appendChild(badge);
  });
}

function updateDots(progress) {
  const dots = stageEl.querySelectorAll(".level-dot");
  dots.forEach((d) => {
    const id = Number(d.getAttribute("data-level-id"));
    d.classList.toggle("locked", id > progress.unlocked);
    d.classList.toggle("completed", id < progress.current);
  });
}

// Устанавливаем позицию кота по уровню
function placeCatAtLevel(levelId) {
  const lvl = LEVELS.find(l => l.id === levelId) || LEVELS[0];
  // перевод % в px от контейнера
  const rect = stageEl.getBoundingClientRect();
  const x = (lvl.x / 100) * rect.width;
  const y = (lvl.y / 100) * rect.height;
  catEl.style.left = `${x}px`;
  catEl.style.top  = `${y}px`;
}

// Анимация перемещения кота к целевому уровню
let moving = false;
function moveCatToLevel(targetLevelId, onDone) {
  if (moving) return;
  const fromId = getProgress().current;
  if (fromId === targetLevelId) { onDone && onDone(); return; }

  const rect = stageEl.getBoundingClientRect();
  const from = LEVELS.find(l => l.id === fromId);
  const to   = LEVELS.find(l => l.id === targetLevelId);
  const start = { x: (from.x/100)*rect.width, y: (from.y/100)*rect.height };
  const end   = { x: (to.x/100)*rect.width,   y: (to.y/100)*rect.height };

  const duration = 800 + 150 * Math.hypot(end.x - start.x, end.y - start.y) / 100; // чуть дальше — чуть дольше
  const t0 = performance.now();
  moving = true;

  function frame(now) {
    const t = Math.min(1, (now - t0) / duration);
    // ease in-out
    const k = t < 0.5 ? 2*t*t : -1 + (4 - 2*t) * t;

    const x = start.x + (end.x - start.x) * k;
    const y = start.y + (end.y - start.y) * k;
    catEl.style.left = `${x}px`;
    catEl.style.top  = `${y}px`;

    // лёгкий наклон в сторону движения
    const angle = Math.atan2(end.y - start.y, end.x - start.x);
    catEl.style.rotate = `${(k === 1 ? 0 : Math.sin(angle)*4)}deg`;

    if (t < 1) requestAnimationFrame(frame);
    else {
      moving = false;
      catEl.style.rotate = "0deg";
      onDone && onDone();
    }
  }
  requestAnimationFrame(frame);
}

function onLevelClick(lvl) {
  const progress = getProgress();
  if (lvl.id > progress.unlocked) {
    // можно всплывашку «уровень ещё закрыт»
    shakeDot(lvl.id);
    return;
  }

  // Двигаемся и по приезду — модалка
  moveCatToLevel(lvl.id, () => {
    // Обновляем текущее и при необходимости — открываем следующий
    const p = getProgress();
    p.current = lvl.id;
    if (p.unlocked < lvl.id + 1 && lvl.id < LEVELS.length) p.unlocked = lvl.id + 1;
    setProgress(p);
    openLevelModal(lvl);
  });
}

function shakeDot(levelId) {
  const dot = stageEl.querySelector(`.level-dot[data-level-id="${levelId}"]`);
  if (!dot) return;
  dot.animate(
    [{ transform: "translate(-50%, -50%)" }, { transform: "translate(-50%, -50%) translateX(-4px)" }, { transform: "translate(-50%, -50%) translateX(4px)" }, { transform: "translate(-50%, -50%)" }],
    { duration: 280 }
  );
}

function openLevelModal(lvl) {
  modalTitle.textContent = lvl.title;
  modalDesc.textContent = lvl.desc || "Описание уровня";
  modalStart.href = lvl.lessonUrl || "#";
  modal.setAttribute("aria-hidden", "false");
}
function closeLevelModal() {
  modal.setAttribute("aria-hidden", "true");
}

modalClose.addEventListener("click", closeLevelModal);
modalCancel.addEventListener("click", closeLevelModal);
modal.addEventListener("click", (e) => { if (e.target === modal) closeLevelModal(); });

resetBtn.addEventListener("click", () => {
  setProgress({ current: 1, unlocked: 1 });
  placeCatAtLevel(1);
});

function init() {
  createLevelDots();
  const p = getProgress();
  updateDots(p);
  updateHUD(p);
  placeCatAtLevel(p.current);

  // Перерасчёт позиции кота при ресайзе (чтобы % → px заново пересчитать)
  window.addEventListener("resize", () => placeCatAtLevel(getProgress().current));
}
document.addEventListener("DOMContentLoaded", init);
