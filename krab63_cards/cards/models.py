from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Card(models.Model):
    """Модель карты."""
    EXPIRED = 'Просрочена'
    ACTIVE = 'Активирована'
    NOT_ACTIVE = 'Не активирована'
    STATUS_CHOICES = (
        (EXPIRED, EXPIRED),
        (ACTIVE, ACTIVE),
        (NOT_ACTIVE, NOT_ACTIVE),
    )

    series = models.IntegerField(
        verbose_name='Серия карты', validators=[
            MaxValueValidator(9999),
            MinValueValidator(1),
        ]
    )
    number = models.IntegerField(
        verbose_name='Номер карты', validators=[
            MaxValueValidator(99999999),
            MinValueValidator(1),
        ]
    )
    issue_date = models.DateTimeField(verbose_name='Дата выпуска')
    expire_date = models.DateTimeField(verbose_name='Дата окончания')
    current_sum = models.FloatField(verbose_name='Остаток на карте')
    status = models.CharField(
        choices=STATUS_CHOICES, default=NOT_ACTIVE, verbose_name='Статус',
        max_length=20,
    )

    def _check_date(self):
        if self.expire_date >= timezone.now():
            return True
        return False

    def get_status(self):
        if not self._check_date():
            self.status = self.EXPIRED
        return self.status

    def activate(self):
        if self._check_date():
            self.status = self.ACTIVE

    def deactivate(self):
        if self._check_date():
            self.status = self.NOT_ACTIVE

    def save(self, *args, **kwargs):
        if not self._check_date():
            self.status = self.EXPIRED
        super(Card, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Карточка'
        verbose_name_plural = 'Карточки'
        ordering = ['series', 'number']
        constraints = [
            models.UniqueConstraint(
                fields=['series', 'number'], name='series_number',
            ),
        ]

    def __str__(self):
        return f'Карточка {self.series} {self.number}'


class Operation(models.Model):
    """Модель операций по карте."""
    card = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name='operations',
    )
    operation_date = models.DateTimeField(verbose_name='Дата операции')
    operation_sum = models.FloatField(verbose_name='Сумма операции')

    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'
        ordering = ['id']

    def __str__(self):
        return f'Операция по карте {self.card}'
