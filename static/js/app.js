// Cursor stickers (emojis) following the pointer
const CP = document.getElementById('cursor-play');
const stickers = ['✨','🧩','⭐','🎈','🐱','🧱'];
let lastTime = 0;
window.addEventListener('pointermove', (e) => {
  const now = performance.now();
  if (now - lastTime < 40) return; // throttle
  lastTime = now;

  const s = document.createElement('div');
  s.className = 'cursor-sticker';
  s.textContent = stickers[Math.floor(Math.random() * stickers.length)];
  s.style.left = e.clientX + 'px';
  s.style.top  = e.clientY + 'px';

  // КЛЮЧ: добавляем в контейнер, у которого pointer-events: none
  (CP || document.body).appendChild(s);

  requestAnimationFrame(() => s.classList.add('fade'));
  setTimeout(() => s.remove(), 700);
});

// Light parallax & confetti
function confettiBurst(ev){
  // Minimal confetti: create 18 pieces around click
  const count = 18;
  for(let i=0;i<count;i++){
    const p = document.createElement('div');
    p.style.position='fixed';
    p.style.left = (ev.clientX)+'px';
    p.style.top  = (ev.clientY)+'px';
    p.style.width='8px'; p.style.height='8px';
    p.style.borderRadius='2px';
    p.style.background = ['#22c55e','#ffa82e','#6ec8ff','#ff74b7','#ff5a7a'][i%5];
    p.style.pointerEvents='none'; p.style.zIndex=200;
    document.body.appendChild(p);
    const ang = (Math.PI*2)*(i/count);
    const dist = 40 + Math.random()*40;
    const dx = Math.cos(ang)*dist;
    const dy = Math.sin(ang)*dist - 20; // a bit up
    p.animate([
      { transform:'translate(0,0)', opacity:1 },
      { transform:`translate(${dx}px, ${dy}px)`, opacity:0 }
    ],{ duration:700+Math.random()*300, easing:'cubic-bezier(.22,.61,.36,1)' }).onfinish = ()=>p.remove();
  }
}
window.confettiBurst = confettiBurst;

// Make course cards slightly tilt & confetti on click
document.querySelectorAll('.course-card').forEach(card=>{
  card.addEventListener('mousemove', e => {
    const r = card.getBoundingClientRect();
    const rx = ((e.clientY - r.top) / r.height - .5) * -6;
    const ry = ((e.clientX - r.left) / r.width  - .5) *  6;
    card.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg)`;
  });
  card.addEventListener('mouseleave', ()=>{
    card.style.transform = 'rotateX(0) rotateY(0)';
  });
  card.addEventListener('click', ev => confettiBurst(ev));
});

// === PATCH: mount animated background layers ===
(function(){
  const bg = document.createElement('div');
  bg.className = 'bg-layer';
  document.body.appendChild(bg);

  const fg = document.createElement('div');
  fg.className = 'fg-floaters';
  document.body.appendChild(fg);

  // Place a few floaters
  const items = [
    {cls:'floater tree',  x:'8vw',  y:'72vh'},
    {cls:'floater tree',  x:'82vw', y:'70vh'},
    {cls:'floater cloud', x:'-10vw',y:'8vh'},
    {cls:'floater cloud', x:'-30vw',y:'18vh'},
    {cls:'floater star',  x:'12vw', y:'16vh'},
    {cls:'floater star',  x:'88vw', y:'22vh'}
  ];
  items.forEach(it=>{
    const el = document.createElement('div');
    el.className = it.cls;
    el.style.left = it.x;
    el.style.top  = it.y;
    fg.appendChild(el);
  });
})();


// Подтягиваем баланс звёзд в шапку на любых страницах
(async function(){
  try{
    const badge = document.getElementById('stars-count');
    if (!badge) return;
    const r = await fetch('/api/v1/me/');
    if (!r.ok) return;
    const me = await r.json();
    badge.textContent = me.stars;
  }catch(e){}
})();