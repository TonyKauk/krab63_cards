from django import forms

from .models import Card


class CardGeneratorForm(forms.Form):
    """Форма для генератора Карт."""
    DURATION_CHOICES = (
        ('1', 'Один месяц'),
        ('6', 'Шесть месяцев'),
        ('12', 'Один год'),
    )
    MAX_QUANTYTY_OF_CARDS = 99999999
    MAX_SERIES_NUMBER = 9999
    MIN_SERIES_NUMBER = 1

    series = forms.IntegerField(
        label='Серия карт', required=True,
    )
    quantity = forms.IntegerField(
        label='Количество карт', required=True,
    )
    duration = forms.ChoiceField(choices=DURATION_CHOICES, required=True)

    def clean_series(self):
        data = self.cleaned_data['series']
        if data > self.MAX_SERIES_NUMBER or data < self.MIN_SERIES_NUMBER:
            raise forms.ValidationError(
                'Номер серии должен быть больше 0 и меньше 10000'
            )
        return data

    def clean_quantity(self):
        data = self.cleaned_data['quantity']
        cards_of_series_used = Card.objects.filter(series=self.series).count()
        cards_of_series_available = (
            self.MAX_QUANTYTY_OF_CARDS - cards_of_series_used
        )
        if cards_of_series_available < self.quantity:
            raise forms.ValidationError(
                'Недостаточно свободных номеров для карт данной серии.'
                f'Доступно {cards_of_series_available} карт данной серии.'
            )
        return data
