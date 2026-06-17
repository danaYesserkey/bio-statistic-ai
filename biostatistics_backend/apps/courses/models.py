import os
import uuid
import mimetypes

from django.utils.text import slugify
from django.db import models
# from polymorphic.models import PolymorphicModel

def get_course_file_upload_path(instance, filename):
    """Генерирует уникальный путь для загрузки файлов"""
    name, ext = os.path.splitext(filename)
    safe_name = slugify(name) or "material"
    unique_filename = f"{uuid.uuid4().hex[:10]}_{safe_name}{ext}"
    
    # Безопасно поднимаемся по связям: Урок -> Модуль -> Курс
    lesson = instance.lesson
    module = lesson.module if hasattr(lesson, 'module') else None
    module_id = module.id if module else 'unknown'
    course_id = module.course_id if (module and hasattr(module, 'course_id')) else 'unknown'
    
    return f"courses/course_{course_id}/modules/module_{module_id}/lessons/lesson_{lesson.id}/{unique_filename}"

class Course(models.Model):
    # Оставляем имя поля как на схеме (course_name)
    course_name = models.CharField(max_length=255)
    # Поле необязательное (на схеме нет NN)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.course_name


class Module(models.Model):
    # Делаем связь ОБЯЗАТЕЛЬНОЙ (как вы верно заметили). 
    # Если курс удаляется — удаляются и его модули.
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    # Имя поля со схемы
    module_name = models.CharField(max_length=255)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.module_name


class Lesson(models.Model):
    # Делаем связь ОБЯЗАТЕЛЬНОЙ. Урок не может существовать без модуля.
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    # Имя поля со схемы
    lesson_name = models.CharField(max_length=255)
    # Имя поля со схемы
    content_kz = models.TextField(blank=True, null=True)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.lesson_name


class Content(models.Model):
    lesson = models.ForeignKey('Lesson', related_name="contents", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, verbose_name="Реттік нөмірі")
    
    # Одно поле для ВСЕХ файлов (pdf, docx, видео, картинки)
    file = models.FileField(upload_to=get_course_file_upload_path, verbose_name="Файл")
    
    # Метаданные (заполняются сами при сохранении)
    original_filename = models.CharField(max_length=255, editable=False, verbose_name="Түпнұсқа файл атауы")
    file_size = models.PositiveBigIntegerField(editable=False, verbose_name="Файл өлшемі (байт)")
    mime_type = models.CharField(max_length=100, editable=False, verbose_name="MIME-түрі")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Қосылған уақыты")

    class Meta:
        ordering = ['order']
        verbose_name = "Контент"
        verbose_name_plural = "Контенттер"

    def save(self, *args, **kwargs):
        # Собираем метаданные только при загрузке нового файла
        if self.file and not self.pk:
            self.original_filename = self.file.name
            self.file_size = self.file.size
            guessed_type, _ = mimetypes.guess_type(self.file.name)
            self.mime_type = guessed_type or "application/octet-stream"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Материал: {self.original_filename} (Урок: {self.lesson})"