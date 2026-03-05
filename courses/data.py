COURSES = [
  {'slug':'scratch-junior','title':'Scratch Junior','tagline':'Игровое знакомство с алгоритмами','color':'#6EC8FF','img':'img/scratch (2).png','theme':'theme-scratchjr',
   'lessons':[
     {'n':1,'title':'Весёлые герои','img':'img/scratchjr_puzzle.png'},
     {'n':2,'title':'Прыжки и смех','img':'img/scratchjr_puzzle.png'},
     {'n':3,'title':'Звуки и эмоции','img':'img/scratchjr_puzzle.png'},
     {'n':4,'title':'Повторы и ритм','img':'img/scratchjr_puzzle.png'},
     {'n':5,'title':'Мини-игра','img':'img/scratchjr_puzzle.png'},
   ]},
  {'slug':'scratch','title':'Scratch','tagline':'Котик и блоки — создаём игры!','color':'#FFA82E','img':'img/scratch (2).png','theme':'theme-scratch',
   'lessons':[
     {'n':1,'title':'Котик оживает','img':'img/scratch_cat.png'},
     {'n':2,'title':'Движение блоками','img':'img/scratch_cat.png'},
     {'n':3,'title':'Если — то!','img':'img/scratch_cat.png'},
     {'n':4,'title':'Циклы-барабаны','img':'img/scratch_cat.png'},
     {'n':5,'title':'Аркада про кота','img':'img/scratch_cat.png'},
   ]},
  {'slug':'roblox','title':'Roblox','tagline':'Кубики, паркур и скрипты','color':'#FF5A7A','img':'img/roblox.png','theme':'theme-roblox',
   'lessons':[
     {'n':1,'title':'Мир из кубиков','img':'img/roblox_cube.png'},
     {'n':2,'title':'Секреты Lua','img':'img/roblox_cube.png'},
     {'n':3,'title':'Ловушки и чекпоинты','img':'img/roblox_cube.png'},
     {'n':4,'title':'UI и таймер','img':'img/roblox_cube.png'},
     {'n':5,'title':'Публикуем уровень','img':'img/roblox_cube.png'},
   ]},
]; COURSES_BY_SLUG={c['slug']:c for c in COURSES}
