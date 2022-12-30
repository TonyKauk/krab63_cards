from datetime import datetime

from django.db import models


class Card(models.Model):
    """Модель карты."""
    series = models.IntegerField(verbose_name='Серия карты')
    number = models.IntegerField(verbose_name='Номер карты')
    issue_date = models.DateTimeField(verbose_name='Дата выпуска')
    expire_date = models.DateTimeField(verbose_name='Дата окончания')
    current_sum = models.FloatField(verbose_name='Остаток на карте')
    status = models.CharField(
        default='Не активирована', verbose_name='Статус',
    )

    def status(self):
        if self._check_date(self) == 'Просрочена':
            return 'Просрочена'
        return self.status

    def _check_date(self):
        if self.expire_date >= datetime.now():
            return 'Не просрочена'
        return 'Просрочена'

    def activate(self):
        if self._check_date(self) == 'Не просрочена':
            self.status = 'Активирована'

    def deactivate(self):
        if self._check_date(self) == 'Не просрочена':
            self.status = 'Деактивирована'

    def save(self, *args, **kwargs):
        if self._check_date(self) == 'Просрочена':
            self.status = 'Просрочена'
        super(Card, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Карточка'
        verbose_name_plural = 'Карточки'
        ordering = ['id']

    def __str__(self):
        return f'Карточка {self.series} {self.number}'


class Operations(models.Model):
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
