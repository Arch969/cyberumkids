# admin.py
from django.contrib import admin
from .models import (
    Profile, Phone, Messenger, ScheduleEntry, StudyAccount, LessonStat,
    Character, DialogueScene, DialogueLine, Teacher
)

from django.utils.html import format_html


# ───────────────── Inlines ─────────────────

class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 1
    fields = ("number",)


class MessengerInline(admin.TabularInline):
    model = Messenger
    extra = 1
    fields = ("type", "login")


class ScheduleEntryInline(admin.TabularInline):
    model = ScheduleEntry
    extra = 1
    fields = ("weekday", "time", "duration_min", "teacher")


class StudyAccountInline(admin.TabularInline):
    model = StudyAccount
    extra = 1
    fields = ("platform", "login", "password")
    # Если захочешь скрыть пароль в списке:
    # readonly_fields = ()


class LessonStatInline(admin.TabularInline):
    model = LessonStat
    extra = 0
    fields = ("date", "title", "homework", "comment")
    ordering = ("-date",)


# ───────────────── Profile Admin ─────────────────

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "username", "full_name", "current_course", "stars", "lessons_balance",
        "age_display", "created_at"
    )
    list_filter = ("gender", "current_course", "created_at")
    search_fields = (
        "username", "display_name", "first_name", "last_name", "middle_name",
        "phones__number", "messengers__login"
    )
    inlines = [PhoneInline, MessengerInline, ScheduleEntryInline, StudyAccountInline, LessonStatInline]

    fieldsets = (
        ("Учетная запись", {
            "fields": ("username", "display_name", "avatar_url", "stars", "lessons_balance")
        }),
        ("Личные данные", {
            "fields": ("last_name", "first_name", "middle_name", "gender", "birth_date")
        }),
        ("Обучение", {
            "fields": ("current_course", "parent_goal", "trial_comment", "progress")
        }),
        ("Служебное", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ("created_at",)

    def full_name(self, obj):
        parts = [obj.last_name, obj.first_name, obj.middle_name]
        return " ".join([p for p in parts if p]).strip() or obj.display_name

    full_name.short_description = "ФИО"

    def age_display(self, obj):
        a = obj.age()
        return a if a is not None else "—"

    age_display.short_description = "Возраст"


# ───────────────── Dialogue Admin (оставляем как было) ─────────────────

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_side')
    list_filter = ('default_side',)
    search_fields = ('name',)


class DialogueLineInline(admin.TabularInline):
    model = DialogueLine
    extra = 0
    fields = ('order', 'character', 'character_name', 'side', 'avatar_override',
              'text', 'typing_speed_ms', 'pause_after_ms', 'audio', 'volume', 'bg_override')


@admin.register(DialogueScene)
class DialogueSceneAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'use_bg', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [DialogueLineInline]


@admin.register(DialogueLine)
class DialogueLineAdmin(admin.ModelAdmin):
    list_display = ('scene', 'order', 'character', 'character_name', 'side')
    list_filter = ('scene', 'side')
    search_fields = ('text', 'character__name', 'character_name')


# ───────────────── (опционально) прямой доступ к связанным моделям ─────────────────
@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ("profile", "number")
    search_fields = ("number", "profile__username", "profile__last_name")


@admin.register(Messenger)
class MessengerAdmin(admin.ModelAdmin):
    list_display = ("profile", "type", "login")
    list_filter = ("type",)
    search_fields = ("login", "profile__username", "profile__last_name")


@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ("profile", "weekday", "time")
    list_filter = ("weekday",)
    search_fields = ("profile__username", "profile__last_name")


@admin.register(StudyAccount)
class StudyAccountAdmin(admin.ModelAdmin):
    list_display = ("profile", "platform", "login")
    search_fields = ("platform", "login", "profile__username", "profile__last_name")


@admin.register(LessonStat)
class LessonStatAdmin(admin.ModelAdmin):
    list_display = ("profile", "date", "title")
    list_filter = ("date",)
    search_fields = ("title", "comment", "homework", "profile__username", "profile__last_name")
    ordering = ("-date",)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display  = ("username", "display_name", "is_active", "students_count", "created_at")
    list_filter   = ("is_active",)
    search_fields = ("username", "display_name", "email", "students__last_name", "students__first_name")
    filter_horizontal = ("students",)  # удобный выбор учеников
    list_display = ("username", "display_name", "is_active", "students_count", "created_at")
    readonly_fields = ("api_token", "created_at", "avatar_preview")
    fieldsets = (
        ("Учетная запись", {"fields": ("username", "display_name", "email", "is_active")}),
        ("API-доступ", {"fields": ("api_token",)}),
        ("Zoom", {"fields": ("zoom_link", "zoom_meeting_id", "zoom_passcode")}),  # NEW
        ("Ученики", {"fields": ("students",)}),
        ("Служебное", {"fields": ("created_at",)}),
        ("Фото",           {"fields": ("photo", "avatar_preview")}),

    )

    def students_count(self, obj):
        return obj.students.count()
    students_count.short_description = "Ученики"

    def avatar_thumb(self, obj):
        if getattr(obj, "photo", None):
            return format_html('<img src="{}" style="width:36px;height:36px;border-radius:50%;object-fit:cover" />', obj.photo.url)
        return "—"
    avatar_thumb.short_description = "Фото"

    def avatar_preview(self, obj):
        if getattr(obj, "photo", None):
            return format_html('<img src="{}" style="width:120px;height:120px;border-radius:20px;object-fit:cover;border:2px solid #E2E8F0" />', obj.photo.url)
        return "—"
    avatar_preview.short_description = "Превью"