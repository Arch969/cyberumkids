let needUserGesture = false;
let pendingLine = null; // сюда положим текущую реплику, если play() заблокирован


(function(){
  const lines = Array.isArray(window.DIALOGUE_LINES) ? window.DIALOGUE_LINES : [];

  // Элементы
  const root   = document.getElementById('dialogue-root');
  const bgEl   = document.getElementById('dlg-bg');
  const leftEl = document.getElementById('avatar-left');
  const rightEl= document.getElementById('avatar-right');
  const nameEl = document.getElementById('dlg-name');
  const textEl = document.getElementById('dlg-text');
  const nextBt = document.getElementById('dlg-next');
  const skipBt = document.getElementById('dlg-skip');
  const autoCb = document.getElementById('dlg-autoplay');
  const barEl  = document.getElementById('dlg-bar');

  // Выставляем корректные размеры области под шапкой
  function measureHeader() {
    const hdr = document.querySelector('.site-header');
    const hdrH = hdr ? hdr.offsetHeight : 64;
    document.documentElement.style.setProperty('--hdr-h', hdrH + 'px');
  }
  function measureBar() {
    const barH = barEl ? barEl.offsetHeight : 180;
    document.documentElement.style.setProperty('--bar-h', barH + 'px');
  }
  measureHeader();
  measureBar();
  window.addEventListener('resize', () => { measureHeader(); measureBar(); });

  // Состояние
  let idx = 0, typing = false, cancelTyping = null, audio = null;

  function setBG(url) {
    if (!bgEl) return;
    if (url) bgEl.style.backgroundImage = `url('${url}')`;
    else     bgEl.style.backgroundImage = 'none';
  }

  function setAvatar(side, url) {
    const el    = side === 'right' ? rightEl : leftEl;
    const other = side === 'right' ? leftEl  : rightEl;
    if (other) other.classList.remove('show');
    if (!el) return;
    if (url) { el.style.backgroundImage = `url('${url}')`; el.classList.add('show'); }
    else     { el.style.backgroundImage = ''; el.classList.remove('show'); }
  }

  async function typeText(str, speed) {
    typing = true;
    textEl.textContent = '';
    let i = 0;
    let stopped = false;
    cancelTyping = () => { stopped = true; textEl.textContent = str; typing = false; };
    while (i < str.length && !stopped) {
      textEl.textContent += str[i++];
      await new Promise(r => setTimeout(r, speed));
    }
    typing = false;
  }

  function stopAudio() { if (audio) { audio.pause(); audio = null; } }

  async function playLine(i) {
    if (i < 0 || i >= lines.length) return;
    const L = lines[i];
    setBG(L.bg || '');
    setAvatar(L.side || 'left', L.avatar || '');
    nameEl.textContent = L.name || '';
    stopAudio();
    if (L.audio) {
      audio = new Audio(L.audio);
      audio.preload = 'auto';
      audio.volume = Math.max(0, Math.min(1, L.volume ?? 1));
      const p = audio.play();
      if (p && typeof p.catch === 'function') {
        p.catch(() => {
          // Браузер запретил автоплей без жеста — запомним реплику и дождёмся первого клика/клавиши
          needUserGesture = true;
          pendingLine = L;
        });
      }
    }

    await typeText(L.text || '', Math.max(5, L.typingSpeed || 18));

    // АВТОПЛЕЙ: после паузы переходим дальше, если включено
    if (autoCb && autoCb.checked) {
      const pause = Math.max(0, L.pauseAfter ?? 400);
      await new Promise(r => setTimeout(r, pause));
      goNext(true);
    }
  }

  function finishDialogue() {
    // По умолчанию — «выйти»: сначала пытаемся вернуться назад,
    // если нельзя — идём на /courses/
    if (window.history.length > 1) {
      window.history.back();
    } else {
      window.location.href = '/courses/';
    }
  }

  async function goNext(fromAutoplay=false) {
    if (typing && cancelTyping) { cancelTyping(); return; }
    idx++;
    if (idx >= lines.length) {
      stopAudio();
      nextBt.disabled = true;
      finishDialogue();
      return;
    }
    await playLine(idx);
  }

  // События
  nextBt.addEventListener('click', () => goNext(false));
  skipBt.addEventListener('click', finishDialogue);
  window.addEventListener('keydown', (e) => {
    if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); nextBt.click(); }
    if (e.key.toLowerCase() === 's' && typing && cancelTyping) { cancelTyping(); }
  });

  // Автоплей включён по умолчанию
  if (root && root.dataset.autoplay === '1' && autoCb) autoCb.checked = false;
    function unlockAudioIfNeeded() {
      if (!needUserGesture || !pendingLine) return;
      needUserGesture = false;
      const L = pendingLine; pendingLine = null;
      try { stopAudio(); } catch(e){}
      audio = new Audio(L.audio);
      audio.preload = 'auto';
      audio.volume = Math.max(0, Math.min(1, L.volume ?? 1));
      audio.play().catch(() => {}); // после первого жеста браузер уже разрешит
    }

    // Любой жест пользователя «разблокирует» звук
    window.addEventListener('pointerdown', unlockAudioIfNeeded, { once: true });
    window.addEventListener('keydown',      unlockAudioIfNeeded, { once: true });
  // Старт
  if (lines.length) playLine(idx);
})();
