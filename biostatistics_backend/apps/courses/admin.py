from django.contrib import admin
from polymorphic.admin import StackedPolymorphicInline, PolymorphicInlineSupportMixin

from .models import Course, Module, Lesson, TextContent, ImageContent, VideoContent, Content


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_name', 'description')
    search_fields = ('course_name',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'module_name', 'course', 'order')
    search_fields = ('module_name',)
    list_filter = ('course',)

# Content
class ContentInline(StackedPolymorphicInline):
    class TextContentInline(StackedPolymorphicInline.Child):
        model = TextContent
    
    class ImageContentInline(StackedPolymorphicInline.Child):
        model = ImageContent
    
    class VideoContentInline(StackedPolymorphicInline.Child):
        model = VideoContent
    
    model = Content
    child_inlines = (
        TextContentInline,
        ImageContentInline,
        VideoContentInline,
    )


@admin.register(Lesson)
class LessonAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    list_display = ('id', 'lesson_name', 'module', 'order')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('lesson_name', 'module', 'order')
        }),
        ('Контент урока', {
            'fields': ('content_kz',),
        }),
    )

    inlines = (ContentInline,)