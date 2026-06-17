from django.contrib import admin
from adminsortable2.admin import SortableStackedInline, SortableAdminBase

from apps.courses.models import Course, Module, Lesson, Content
from apps.quizzes.models import Quiz

class ModuleInline(SortableStackedInline):
    model = Module
    extra = 0
    show_change_link = True

@admin.register(Course)
class CourseAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ('id', 'course_name', 'description')
    search_fields = ('course_name',)
    inlines = [ModuleInline]

class LessonInline(SortableStackedInline):
    model = Lesson
    extra = 0
    fields = ('lesson_name',)
    show_change_link = True

@admin.register(Module)
class ModuleAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ('id', 'module_name', 'course', 'order')
    search_fields = ('module_name',)
    list_filter = ('course',)
    inlines = [LessonInline]
    fields = ('course', 'module_name',)


# --- МАТЕРИАЛЫ УРОКА (Вместо старых полиморфных инлайнов) ---
class ContentInline(SortableStackedInline):
    model = Content
    extra = 0
    # Поля, которые препод будет видеть/заполнять при добавлении файла прямо в уроке
    fields = ('file', 'order', 'original_filename', 'file_size', 'mime_type')
    # Метаданные защищаем от редактирования руками
    readonly_fields = ('original_filename', 'file_size', 'mime_type')


class QuizInline(admin.TabularInline):
    model = Quiz
    extra = 0
    show_change_link = True


@admin.register(Lesson)
class LessonAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ('id', 'lesson_name', 'module', 'order')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('module', 'lesson_name',)
        }),
    )

    inlines = (QuizInline, ContentInline)