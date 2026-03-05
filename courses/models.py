from django.db import models
from django.utils import timezone
import secrets


class Profile(models.Model):
    # базовое
    username     = models.CharField(max_length=150, unique=True)
    display_name = models.CharField(max_length=150, blank=True, default='')
    stars        = models.PositiveIntegerField(default=25)
    progress     = models.JSONField(default=dict, blank=True)
    avatar_url   = models.URLField(blank=True, default='')
    created_at   = models.DateTimeField(default=timezone.now)

    # новое
    first_name   = models.CharField("Имя", max_length=100, blank=True)
    last_name    = models.CharField("Фамилия", max_length=100, blank=True)
    middle_name  = models.CharField("Отчество", max_length=100, blank=True)
    gender       = models.CharField("Пол", max_length=10, choices=[("M","Мальчик"),("F","Девочка")], blank=True)
    birth_date   = models.DateField("Дата рождения", blank=True, null=True)

    # баланс уроков
    lessons_balance = models.PositiveIntegerField("Баланс уроков", default=0)

    # текущий курс
    COURSE_CHOICES = [
        ("scratch-junior","Scratch Junior"),
        ("scratch","Scratch"),
        ("roblox","Roblox"),
        ("blockbench","Blockbench"),
        ("blender","Blender"),
        ("unity","Unity"),
        ("python-basic","Python basic"),
        ("pygame","Pygame"),
        ("telegram-bots","Telegram bots"),
        ("olympiad-python","Olympiad python"),
        ("web-dev","Web dev"),
        ("computer-literacy","Computer literacy"),
        ("block-python","Block python"),
        ("figma-tilda","Figma Tilda"),
    ]
    current_course = models.CharField("Текущий курс", max_length=50, choices=COURSE_CHOICES, blank=True)

    parent_goal  = models.TextField("Цели обучения (комментарий родителя)", blank=True)
    trial_comment= models.TextField("Комментарий пробного занятия", blank=True)

    def age(self):
        """Вычислить возраст от birth_date"""
        import datetime
        if not self.birth_date:
            return None
        today = datetime.date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def __str__(self):
        return f"{self.display_name or self.username} ({self.stars}★)"


# ── Контакты ───────────────────────────

class Phone(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="phones")
    number  = models.CharField("Телефон", max_length=30)

class Messenger(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="messengers")
    M_CHOICES = [("tg","Telegram"),("wa","WhatsApp"),("vk","ВКонтакте"),("mx","MAX")]
    type    = models.CharField(max_length=10, choices=M_CHOICES)
    login   = models.CharField(max_length=100)

# ── Расписание ─────────────────────────

class ScheduleEntry(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="schedule")
    weekday = models.IntegerField("День недели", choices=[(i, d) for i,d in enumerate(
        ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
    )])
    time    = models.TimeField("Время начала")

# ── Учебные аккаунты ──────────────────

class StudyAccount(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="study_accounts")
    platform= models.CharField("Платформа", max_length=100)
    login   = models.CharField(max_length=100)
    password= models.CharField(max_length=100)

# ── Статистика уроков ─────────────────

class LessonStat(models.Model):
    profile  = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="lessons_stats")
    title    = models.CharField("Тема урока", max_length=200)
    homework = models.TextField("Домашнее задание", blank=True)
    comment  = models.TextField("Комментарий учителя", blank=True)
    date     = models.DateField("Дата проведения", default=timezone.now)


# ── Базовый выбор стороны ───────────────────────────────────────────────
SIDE_CHOICES = (
    ('left',  'Слева'),
    ('right', 'Справа'),
)

class Character(models.Model):
    """Повторно используемый персонаж (опционально)."""
    name        = models.CharField(max_length=100, unique=True)
    avatar      = models.ImageField(upload_to='dialogue/avatars/', blank=True, null=True,
                                    help_text='PNG с прозрачностью 512x512, будет поставлен внизу слева/справа.')
    default_side= models.CharField(max_length=5, choices=SIDE_CHOICES, default='left')

    def __str__(self):
        return self.name

class DialogueScene(models.Model):
    """Сцена диалога (страница с последовательностью реплик)."""
    slug        = models.SlugField(max_length=120, unique=True)
    title       = models.CharField(max_length=200)
    use_bg      = models.BooleanField(default=False, help_text='Включить фон для сцены')
    background  = models.ImageField(upload_to='dialogue/backgrounds/', blank=True, null=True)
    created_at  = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class DialogueLine(models.Model):
    """Отдельная реплика в сцене."""
    scene       = models.ForeignKey(DialogueScene, on_delete=models.CASCADE, related_name='lines')
    order       = models.PositiveIntegerField(default=1, help_text='Порядок в сцене (сортировка по возрастанию)')
    # Персонаж можно выбрать из справочника или задать вручную:
    character   = models.ForeignKey(Character, on_delete=models.SET_NULL, blank=True, null=True)
    character_name = models.CharField(max_length=100, blank=True, default='',
        help_text='Если пусто — будет использовано имя персонажа из справочника')
    side        = models.CharField(max_length=5, choices=SIDE_CHOICES, default='left',
        help_text='С какой стороны появится аватар на экране для этой реплики')
    avatar_override = models.ImageField(upload_to='dialogue/line_avatars/', blank=True, null=True,
        help_text='Опционально: переопределить аватар именно для этой реплики')

    text        = models.TextField(help_text='Текст реплики (будет печататься по символам)')
    typing_speed_ms = models.PositiveIntegerField(default=18, help_text='Скорость печати (мс на символ)')
    pause_after_ms  = models.PositiveIntegerField(default=400, help_text='Пауза после завершения печати')

    audio       = models.FileField(upload_to='dialogue/audio/', blank=True, null=True,
        help_text='Опционально: аудио, воспроизводится вместе с печатью')
    volume      = models.FloatField(default=1.0, help_text='Громкость 0.0—1.0')

    bg_override = models.ImageField(upload_to='dialogue/line_backgrounds/', blank=True, null=True,
        help_text='Опционально: фон только на время этой реплики')

    class Meta:
        ordering = ['order']

    def __str__(self):
        nm = self.character_name or (self.character.name if self.character else 'Персонаж')
        return f'[{self.order}] {nm}: {self.text[:32]}…'

    # Удобные геттеры
    def get_name(self):
        return self.character_name or (self.character.name if self.character else '')

    def get_side(self):
        return self.side or (self.character.default_side if self.character else 'left')

    def get_avatar_url(self):
        src = self.avatar_override or (self.character.avatar if self.character else None)
        return src.url if src else ''




class Teacher(models.Model):
    """Учитель, к которому будут привязаны ученики (Profile)."""
    username      = models.CharField(max_length=150, unique=True)
    display_name  = models.CharField("Имя для отображения", max_length=150, blank=True, default="")
    email         = models.EmailField(blank=True, default="")
    is_active     = models.BooleanField(default=True)
    # Простейшая токен-аутентификация для API учителя:
    api_token     = models.CharField(max_length=64, unique=True, editable=False)

    photo         = models.ImageField("Фото", upload_to="teachers/photos/", blank=True, null=True)
    zoom_link = models.URLField("Zoom-ссылка", blank=True, default="")
    zoom_meeting_id = models.CharField("ID конференции", max_length=64, blank=True, default="")
    zoom_passcode = models.CharField("Пароль конференции", max_length=64, blank=True, default="")

    # Связь с учениками (многие-ко-многим)
    students      = models.ManyToManyField('Profile', related_name='teachers', blank=True)





    created_at    = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.display_name or self.username

    def rotate_token(self, save=True):
        """Сгенерировать новый токен."""
        self.api_token = secrets.token_hex(24)  # 48 hex chars
        if save:
            self.save(update_fields=["api_token"])
        return self.api_token

    def save(self, *args, **kwargs):
        if not self.api_token:
            self.rotate_token(save=False)
        super().save(*args, **kwargs)


class ScheduleEntry(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="schedule")
    weekday = models.IntegerField("День недели", choices=[(i, d) for i,d in enumerate(["Пн","Вт","Ср","Чт","Пт","Сб","Вс"])])
    time    = models.TimeField("Время начала")
    duration_min = models.PositiveIntegerField("Длительность (мин)", default=60)
    teacher = models.ForeignKey('Teacher', null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='schedule_entries', verbose_name="Учитель")