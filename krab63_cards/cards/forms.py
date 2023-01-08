from django import forms

from .models import Card


class CardSearchForm(forms.Form):
    """Форма поиска среди Карт."""

    EXPIRED = 'Просрочена'
    ACTIVE = 'Активирована'
    NOT_ACTIVE = 'Не активирована'
    ANY = 'Любой'
    STATUS_CHOICES = (
        (EXPIRED, EXPIRED),
        (ACTIVE, ACTIVE),
        (NOT_ACTIVE, NOT_ACTIVE),
        (ANY, ANY),

    )

    series = forms.IntegerField(label='Серия карты', required=False)
    number = forms.IntegerField(label='Номер карты', required=False)
    issue_date = forms.DateField(
        label='Дата выпуска карты', required=False,
        widget=forms.DateInput(attrs=dict(type='date')),
    )
    expire_date = forms.DateField(
        label='Окончание срока действия карты', required=False,
        widget=forms.DateInput(attrs=dict(type='date')),
    )
    status = forms.TypedChoiceField(
        label='Cтатус', choices=STATUS_CHOICES, required=False,
        coerce=int,
    )


class CardGeneratorForm(forms.Form):
    """Форма для генератора Карт."""

    DURATION_CHOICES = (
        ('1', 'Один месяц'),
        ('6', 'Шесть месяцев'),
        ('12', 'Один год'),
    )
    MAX_QUANTYTY_OF_CARDS = 99999999
    MAX_SERIES = 9999
    MIN_SERIES = 1

    series = forms.IntegerField(label='Серия карт', required=False)
    quantity = forms.IntegerField(label='Количество карт', required=False)
    duration = forms.TypedChoiceField(
        label='Срок действия', choices=DURATION_CHOICES, required=True,
        coerce=int,
    )

    def clean_series(self):
        data = self.cleaned_data['series']
        if not data:
            raise forms.ValidationError(
                'Номер серии обязательно должен быть указан'
            )
        if data > self.MAX_SERIES or data < self.MIN_SERIES:
            raise forms.ValidationError(
                'Номер серии должен быть больше 0 и меньше 10000'
            )
        return data

    def clean_quantity(self):
        try:
            series = self.cleaned_data['series']
        except KeyError:
            raise forms.ValidationError(
                'Для проверки доступности указанного количества нужно ввести '
                'корректную серию'
            )
        data = self.cleaned_data['quantity']
        if not data:
            raise forms.ValidationError(
                'Количество карт обязательно должно быть указано'
            )
        cards_of_series_used = Card.objects.filter(series=series).count()
        cards_of_series_available = (
            self.MAX_QUANTYTY_OF_CARDS - cards_of_series_used
        )
        if cards_of_series_available < data:
            raise forms.ValidationError(
                'Недостаточно свободных номеров для карт данной серии.'
                f'Доступно {cards_of_series_available} карт данной серии.'
            )
        return data
