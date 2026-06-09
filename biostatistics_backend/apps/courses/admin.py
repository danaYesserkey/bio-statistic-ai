from django.contrib import admin
from polymorphic.admin import StackedPolymorphicInline, PolymorphicInlineSupportMixin
from adminsortable2.admin import SortableStackedInline, SortableTabularInline, SortableAdminBase

from .models import Course, Module, Lesson, TextContent, ImageContent, VideoContent, Content


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

# Content
class ContentInline(StackedPolymorphicInline):
    class TextContentInline(StackedPolymorphicInline.Child):
        model = TextContent
        fields = ('content',)
    
    class ImageContentInline(StackedPolymorphicInline.Child):
        model = ImageContent
        fields = ('content_url',)
    
    class VideoContentInline(StackedPolymorphicInline.Child):
        model = VideoContent
        fields = ('content_url',)
    
    model = Content
    child_inlines = (
        TextContentInline,
        ImageContentInline,
        VideoContentInline,
    )

class ContentOrderInline(SortableStackedInline):
    model = Content
    extra = 0
    can_delete = False
    verbose_name_plural = 'Content order'

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Lesson)
class LessonAdmin(SortableAdminBase, PolymorphicInlineSupportMixin, admin.ModelAdmin):
    list_display = ('id', 'lesson_name', 'module', 'order')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('module', 'lesson_name',)
        }),
    )

    inlines = (ContentOrderInline, ContentInline,)