from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .data import COURSES, COURSES_BY_SLUG
from django.shortcuts import get_object_or_404
from .models import Profile, Teacher
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token

from .models import DialogueScene

from django.utils import timezone
import datetime
import calendar as pycal
from .models import ScheduleEntry
from django.apps import apps

SESSION_KEY='kid_is_auth'
SESSION_PROFILEID = 'kid_profile_id'    # новый

def _get_profile(request):
    pid = request.session.get(SESSION_PROFILEID)
    if pid:
        try:
            return Profile.objects.get(id=pid)
        except Profile.DoesNotExist:
            pass
    return None



@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        if login == 'admin' and password == 'admin':
            request.session[SESSION_KEY] = True
            # создаём/получаем профиль (для демо — username=admin)
            profile, _ = Profile.objects.get_or_create(
                username=login,
                defaults={"display_name": "Юный программист", "stars": 25,
                          "progress": {"scratch-junior":{"done":[],"total":5},
                                       "scratch":{"done":[],"total":5},
                                       "roblox":{"done":[],"total":5}}}
            )
            request.session[SESSION_PROFILEID] = profile.id
            return redirect('courses_index')
        return render(request, 'login.html', {'error': 'Неверные данные'})
    if request.session.get(SESSION_KEY):
        return redirect('courses_index')
    return render(request, 'login.html')

def logout_view(request):
    request.session.pop(SESSION_KEY, None)
    return redirect('login')

def _need_login(request): return not request.session.get(SESSION_KEY)

def courses_index(request):
    if _need_login(request): return redirect('login')
    return render(request,'courses_index.html',{'courses':COURSES})

def course_detail(request, slug):
    if _need_login(request): return redirect('login')
    course = COURSES_BY_SLUG.get(slug)
    if not course: return redirect('courses_index')
    return render(request,'course_detail.html',{'course':course})

def api_courses(request):
    return JsonResponse({'courses':[{'slug':c['slug'],'title':c['title'],'tagline':c['tagline'],'theme':c['theme']} for c in COURSES]})

def api_course_lessons(request, slug):
    c = COURSES_BY_SLUG.get(slug)
    if not c: return JsonResponse({'detail':'not found'}, status=404)
    return JsonResponse({'lessons':c['lessons']})


def cabinet_view(request):
    if not request.session.get(SESSION_KEY):
        return redirect('login')
    profile = _get_profile(request)
    if not profile:
        return redirect('logout')
    # простая агрегация
    total_lessons = sum(v.get("total", 0) for v in profile.progress.values())
    done_lessons  = sum(len(v.get("done", [])) for v in profile.progress.values())
    completion = round((done_lessons / total_lessons) * 100, 1) if total_lessons else 0.0
    return render(request, 'cabinet.html', {
        "profile": profile,
        "stats": {
            "total_lessons": total_lessons,
            "done_lessons": done_lessons,
            "completion": completion,
        }
    })

@require_POST
def earn_stars(request):
    """Демо-начисление: +5 звёзд (можно вызвать fetch'ем из карточек/урока)."""
    if not request.session.get(SESSION_KEY):
        return JsonResponse({"detail": "auth required"}, status=401)
    profile = _get_profile(request)
    if not profile:
        return JsonResponse({"detail": "profile not found"}, status=404)
    inc = int(request.POST.get("inc", 5))
    profile.stars += max(0, inc)
    profile.save(update_fields=["stars"])
    return JsonResponse({"stars": profile.stars})

def api_me(request):
    if not request.session.get(SESSION_KEY):
        return JsonResponse({"detail": "auth required"}, status=401)
    p = _get_profile(request)
    if not p:
        return JsonResponse({"detail": "profile not found"}, status=404)
    return JsonResponse({
        "username": p.username,
        "display_name": p.display_name,
        "stars": p.stars,
        "progress": p.progress,
        "csrftoken": get_token(request),  # удобно для fetch POST
    })



def dialogue_scene(request, slug):
    """Страница проигрывателя диалога."""
    scene = get_object_or_404(DialogueScene, slug=slug)
    # Подготовим сериализацию для JS
    lines = []
    for ln in scene.lines.all():
        lines.append({
            'order': ln.order,
            'name': ln.get_name(),
            'side': ln.get_side(),  # 'left' | 'right'
            'avatar': ln.get_avatar_url(),
            'text': ln.text,
            'typingSpeed': ln.typing_speed_ms,
            'pauseAfter': ln.pause_after_ms,
            'audio': ln.audio.url if ln.audio else '',
            'volume': ln.volume,
            'bg': ln.bg_override.url if ln.bg_override else (scene.background.url if scene.use_bg and scene.background else ''),
        })
    return render(request, 'dialogue_scene.html', {
        'scene': scene,
        'lines_json': lines,   # положим готовым списком (в шаблоне превратим в JSON)
    })








def _auth_teacher(request):
    """Простая токен-аутентификация для учителя по заголовку X-API-KEY."""
    token = request.headers.get('X-API-KEY') or request.META.get('HTTP_X_API_KEY')
    if not token:
        return None
    try:
        return Teacher.objects.get(api_token=token, is_active=True)
    except Teacher.DoesNotExist:
        return None

@require_http_methods(["GET"])
def api_teacher_students(request):
    """
    Вернуть список учеников, прикреплённых к учителю.
    Авторизация: заголовок X-API-KEY: <teacher.api_token>
    Ответ: { "teacher": {...}, "students": [...] }
    """
    teacher = _auth_teacher(request)
    if not teacher:
        return JsonResponse({"detail": "invalid or missing API token"}, status=401)

    # Можно выбрать, какие поля возвращать. Оставим базово и пару полезных полей.
    def student_payload(p: Profile):
        # Собираем телефоны/мессенджеры при наличии моделей
        phones = list(getattr(p, "phones", []).values_list("number", flat=True)) if hasattr(p, "phones") else []
        mess   = []
        if hasattr(p, "messengers"):
            for m in p.messengers.all():
                mess.append({"type": m.type, "login": m.login})

        return {
            "id": p.id,
            "username": p.username,
            "display_name": p.display_name,
            "full_name": " ".join([x for x in [getattr(p, "last_name", ""), getattr(p, "first_name", ""), getattr(p, "middle_name", "")] if x]).strip() or p.display_name,
            "current_course": getattr(p, "current_course", ""),
            "lessons_balance": getattr(p, "lessons_balance", 0),
            "age": p.age() if hasattr(p, "age") else None,
            "phones": phones,
            "messengers": mess,
        }

    qs = teacher.students.select_related().prefetch_related("phones", "messengers").all()
    data = [student_payload(p) for p in qs]

    return JsonResponse({
        "teacher": {
            "id": teacher.id,
            "username": teacher.username,
            "display_name": teacher.display_name,
        },
        "students": data
    })


@require_http_methods(["GET"])
def calendar_view(request):
    if not request.session.get(SESSION_KEY):
        return redirect('login')
    profile = _get_profile(request)
    if not profile:
        return redirect('logout')

    today = timezone.localdate()
    teacher = getattr(profile, "teachers", None).first() if hasattr(profile, "teachers") else None

    return render(request, 'calendar.html', {
        "ym": f"{today.year:04d}-{today.month:02d}",
        "teacher": teacher,  # ← передаём в шаблон
    })

@require_http_methods(["GET"])
def api_my_schedule(request):
    if not request.session.get(SESSION_KEY):
        return JsonResponse({"detail": "auth required"}, status=401)
    profile = _get_profile(request)
    if not profile:
        return JsonResponse({"detail": "profile not found"}, status=404)

    # month=YYYY-MM
    mstr = request.GET.get("month")
    if not mstr:
        d = timezone.localdate()
        year, month = d.year, d.month
    else:
        try:
            year, month = map(int, mstr.split("-"))
        except Exception:
            return JsonResponse({"detail": "bad month format, expected YYYY-MM"}, status=400)

    first_day = datetime.date(year, month, 1)
    _, last_day_num = pycal.monthrange(year, month)
    last_day = datetime.date(year, month, last_day_num)

    events = []

    # Мягкая попытка получить модели, чтобы не падать, если их ещё нет
    ScheduleEntry = apps.get_model('courses', 'ScheduleEntry')  # может вернуть None
    LessonStat    = apps.get_model('courses', 'LessonStat')

    # Название урока из текущего курса
    course_map = {
        "scratch-junior": "Scratch Junior", "scratch": "Scratch", "roblox": "Roblox",
        "blockbench": "Blockbench", "blender": "Blender", "unity": "Unity",
        "python-basic": "Python basic", "pygame": "Pygame", "telegram-bots": "Telegram bots",
        "olympiad-python": "Olympiad python", "web-dev": "Web dev",
        "computer-literacy": "Computer literacy", "block-python": "Block python",
        "figma-tilda": "Figma Tilda",
    }
    base_title = course_map.get(getattr(profile, "current_course", "") or "", "Урок")

    # Регулярка: Пн=0 .. Вс=6
    if ScheduleEntry is not None and hasattr(profile, "schedule"):
        entries = profile.schedule.all().order_by('weekday', 'time')

        def dates_for_weekday(weekday: int):
            shift = (weekday - first_day.weekday()) % 7
            d = first_day + datetime.timedelta(days=shift)
            while d <= last_day:
                yield d
                d += datetime.timedelta(days=7)

        for e in entries:
            duration_min = getattr(e, "duration_min", 60)
            # учитель: из слота, иначе первый прикреплённый к ученику
            t = getattr(e, "teacher", None)
            if t is None and hasattr(profile, "teachers"):
                t = profile.teachers.first()

            t_payload = {
                "teacher_id": t.id if t else None,
                "teacher_name": (t.display_name or t.username) if t else "",
                "teacher_photo": (t.photo.url if (t and getattr(t, "photo", None)) else ""),
                "zoom_link": t.zoom_link if (t and t.zoom_link) else "",
                "zoom_meeting_id": t.zoom_meeting_id if (t and t.zoom_meeting_id) else "",
                "zoom_passcode": t.zoom_passcode if (t and t.zoom_passcode) else "",
            }

            for d in dates_for_weekday(e.weekday):
                start_dt = datetime.datetime.combine(d, e.time)
                end_dt = start_dt + datetime.timedelta(minutes=duration_min)
                events.append({
                    "date": d.isoformat(),
                    "start": start_dt.strftime("%H:%M"),
                    "end": end_dt.strftime("%H:%M"),
                    "kind": "planned",
                    "title": base_title,
                    **t_payload,
                })

    # Пройденные уроки в месяце
    if LessonStat is not None and hasattr(profile, "lessons_stats"):
        for s in profile.lessons_stats.filter(date__gte=first_day, date__lte=last_day).order_by("date"):
            events.append({
                "date": s.date.isoformat(),
                "start": None, "end": None,
                "title": f"Пройдено: {s.title}",
                "kind": "done"
            })

    return JsonResponse({"month": f"{year:04d}-{month:02d}", "events": events})


def scratch_map(request):
    # при желании можно подставлять прогресс пользователя из БД
    return render(request, "scratch_map.html")