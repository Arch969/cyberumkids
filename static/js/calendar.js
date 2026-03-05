(function(){
  const root    = document.getElementById('cal-root');
  const grid    = document.getElementById('cal-grid');
  const titleEl = document.getElementById('cal-title');

  const START_YM = (root?.dataset?.startYm) || '';
  let curYear, curMonth;
  if(START_YM && START_YM.includes('-')){
    curYear  = parseInt(START_YM.split('-')[0], 10);
    curMonth = parseInt(START_YM.split('-')[1], 10);
  } else { const n=new Date(); curYear=n.getFullYear(); curMonth=n.getMonth()+1; }

  // Zoom-данные с сервера (никаких доп. API)
  const ZOOM = {
    teacher_name: root?.dataset?.teacherName || '',
    link:         root?.dataset?.zoomLink   || '',
    meeting_id:   root?.dataset?.zoomId     || '',
    passcode:     root?.dataset?.zoomPass   || ''
  };

  // Модалка
  const modal      = document.getElementById('lesson-modal');
  const modalClose = document.getElementById('cm-close');
  const modalSub   = document.getElementById('cm-subtitle');
  const modalList  = document.getElementById('cm-lessons');

  function ymStr(y,m){ return y.toString().padStart(4,'0')+'-'+m.toString().padStart(2,'0'); }
  function monthNameRu(m){ return ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'][m-1]; }
  function firstOffset(y,m){ const d=new Date(Date.UTC(y,m-1,1)); return (d.getUTCDay()+6)%7; } // Пн=0..Вс=6
  function lastDay(y,m){ return new Date(Date.UTC(y,m,0)).getUTCDate(); }

  async function loadEvents(y,m){
    // используем существующее API /api/v1/my-schedule/ без изменений
    const r = await fetch(`/api/v1/my-schedule/?month=${ymStr(y,m)}`);
    if (!r.ok) return {events:[]};
    return await r.json();
  }

function renderGrid(y,m,payload){
  grid.innerHTML = '';
  titleEl.textContent = `${monthNameRu(m)} ${y}`;

  const daysInMonth = lastDay(y,m);
  const offset = firstOffset(y,m);
  const totalCells = 42;

  const byDate = {};
  (payload.events||[]).forEach(ev=>{
    (byDate[ev.date] = byDate[ev.date] || []).push(ev);
  });

  for(let i=0;i<totalCells;i++){
    const cell = document.createElement('div');
    cell.className = 'cal-cell';

    const dayNum = i - offset + 1;
    if(dayNum>=1 && dayNum<=daysInMonth){
      const yyyy=y.toString().padStart(4,'0'), mm=m.toString().padStart(2,'0'), dd=dayNum.toString().padStart(2,'0');
      const iso=`${yyyy}-${mm}-${dd}`;

      const head = document.createElement('div');
      head.className = 'cal-cell-head';
      head.innerHTML = `<div class="cal-date">${dayNum}</div><div class="cal-weekday"></div>`;

      const list = document.createElement('div');
      list.className = 'cal-events';

      const dayEvents = byDate[iso] || [];
      const planned = dayEvents.filter(e=>e.kind==='planned');
      const done    = dayEvents.filter(e=>e.kind==='done');     // ← NEW

      // Только время старта — крупно по центру
      planned.forEach(ev=>{
        const pill = document.createElement('div');
        pill.className = 'time-pill';
        pill.textContent = ev.start || '';
        list.appendChild(pill);
      });

      cell.appendChild(head);
      if(planned.length) cell.appendChild(list);

      // Рисуем бейдж «пройдено» в углу (если есть)
      if(done.length){
        const box = document.createElement('div');
        box.className = 'done-badges';
        const chip = document.createElement('div');
        chip.className = 'done-chip';
        chip.textContent = done.length > 1 ? `✓×${done.length}` : '✓';
        chip.title = done.map(d=>d.title || 'Пройдено').join('\n');
        box.appendChild(chip);
        cell.appendChild(box);
      }

      // Модалка: и planned, и done
      if(planned.length || done.length){
        cell.style.cursor = 'pointer';
        cell.addEventListener('click', ()=>{
          modalSub.textContent = new Date(iso).toLocaleDateString('ru-RU', { day:'numeric', month:'long', year:'numeric' });
          modalList.innerHTML = '';

          // блок с будущими занятиями (как было — с «Подключиться» и копированием)
          planned.forEach(ev=>{
            const card = document.createElement('div');
            card.className = 'cm-card';

            const hasPhoto = !!(ev.teacher_photo);
            const teacherBlock = `
              <div class="cm-teacher">
                ${hasPhoto ? `<img class="cm-avatar" src="${ev.teacher_photo}" alt="${ev.teacher_name||'Учитель'}">`
                            : `<div class="cm-avatar" aria-hidden="true"></div>`}
                <div><div class="cm-tname">${ev.teacher_name || 'Учитель'}</div></div>
              </div>`;

            card.innerHTML = `
              ${teacherBlock}
              <div class="cm-row"><strong>${ev.start || ''}</strong></div>
              <div class="cm-row">
                <a class="cm-btn" ${ev.zoom_link ? `href="${ev.zoom_link}" target="_blank" rel="noopener"` : 'aria-disabled="true" style="opacity:.5;pointer-events:none"'}>Подключиться к уроку</a>
                <button class="cm-ghost cm-copy" data-copy="${ev.zoom_link||''}">Скопировать ссылку</button>
              </div>
              <div class="cm-row">
                <div class="cm-field">ID: <span>${ev.zoom_meeting_id||'—'}</span></div>
                <button class="cm-copy" data-copy="${ev.zoom_meeting_id||''}">Копировать ID</button>
              </div>
              <div class="cm-row">
                <div class="cm-field">Пароль: <span>${ev.zoom_passcode||'—'}</span></div>
                <button class="cm-copy" data-copy="${ev.zoom_passcode||''}">Копировать пароль</button>
              </div>
            `;
            card.querySelectorAll('.cm-copy').forEach(btn=>{
              btn.addEventListener('click', async ()=>{
                const val = btn.getAttribute('data-copy') || '';
                if(!val) return;
                try{ await navigator.clipboard.writeText(val); const t=btn.textContent; btn.textContent='Скопировано!'; setTimeout(()=>btn.textContent=t,1100);}
                catch(e){ alert('Не удалось скопировать'); }
              });
            });
            modalList.appendChild(card);
          });

          // блок «Пройденные уроки» — компактный список (без кнопок)
          if(done.length){
            const card = document.createElement('div');
            card.className = 'cm-card';
            const items = done.map(d=>`<li>${(d.title||'Пройдено').replace(/^Пройдено:\s*/,'')}</li>`).join('');
            card.innerHTML = `
              <div class="cm-row"><strong>Пройденные уроки</strong></div>
              <ul style="margin:6px 0 0 18px">${items}</ul>
            `;
            modalList.appendChild(card);
          }

          openModal();
        });
      }
    }
    grid.appendChild(cell);
  }
}



  function openModal(){ modal.classList.remove('hidden'); modal.setAttribute('aria-hidden','false'); }
  function closeModal(){ modal.classList.add('hidden'); modal.setAttribute('aria-hidden','true'); }
  document.getElementById('cm-close').addEventListener('click', closeModal);
  document.getElementById('lesson-modal').addEventListener('click', (e)=>{ if(e.target.id==='lesson-modal') closeModal(); });
  document.addEventListener('keydown', (e)=>{ if(e.key === 'Escape') closeModal(); });

  async function refresh(){ const data = await loadEvents(curYear, curMonth); renderGrid(curYear, curMonth, data); }
  document.getElementById('prev-month').addEventListener('click', ()=>{ curMonth--; if(curMonth<1){curMonth=12;curYear--;} refresh(); });
  document.getElementById('next-month').addEventListener('click', ()=>{ curMonth++; if(curMonth>12){curMonth=1;curYear++;} refresh(); });
  document.getElementById('today-month').addEventListener('click', ()=>{ const n=new Date(); curYear=n.getFullYear(); curMonth=n.getMonth()+1; refresh(); });

  refresh();
})();
