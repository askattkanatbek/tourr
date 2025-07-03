from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import datetime


class Tour(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('published', 'Опубликован')
    )

    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='tours/images/', blank=True, null=True, verbose_name='Фото')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(
        verbose_name='Дата окончания'
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tours',
                                   verbose_name='Автор')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey('TourCategory', on_delete=models.CASCADE, related_name='tours')


    def __str__(self):
         return self.title

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("Дата окончания не может быть раньше даты начала")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class TourCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name