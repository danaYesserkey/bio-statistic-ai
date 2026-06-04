from django.contrib import admin

# Register your models here.
from .models import Course, Module, Lesson
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_name', 'description')
    search_fields = ('course_name',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'module_name', 'course', 'order')
    search_fields = ('module_name',)
    list_filter = ('course',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson_name', 'module', 'order')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('lesson_name', 'module', 'order')
        }),
        ('Контент урока', {
            'fields': ('content_kz',),
        }),
    )