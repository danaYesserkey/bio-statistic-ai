from django.db import models
from polymorphic.models import PolymorphicModel

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

    def __str__(self):
        return self.lesson_name


class Content(PolymorphicModel):
    lesson = models.ForeignKey(Lesson, related_name="contents", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.lesson} content"

class TextContent(Content):
    content = models.TextField()

class ImageContent(Content):
    content_url = models.FileField(upload_to="suret/")

class VideoContent(Content):
    content_url = models.FileField(upload_to="beine/")