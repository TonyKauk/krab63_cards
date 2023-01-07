import datetime
from dateutil.relativedelta import relativedelta

from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.utils import timezone
from django.db.models import Window, F
from django.db.models.functions import Lag

from .forms import CardGeneratorForm, CardSearchForm
from .models import Card


class CardListView(generic.ListView):
    """Отображает все Карты."""
    template_name = 'cards/card_list.html'
    context_object_name = 'cards'
    model = Card

    def get_queryset(self):
        series = self.request.GET.get('series', False)
        number = self.request.GET.get('number', False)
        issue_date_text = self.request.GET.get('issue_date', False)
        expire_date_text = self.request.GET.get('expire_date', False)
        status = self.request.GET.get('status', CardSearchForm.ANY)

        cards = self.model.objects.all()

        if series:
            cards = cards.filter(series=series)

        if number:
            cards = cards.filter(number=number)

        if issue_date_text:
            issue_date = datetime.datetime.strptime(
                issue_date_text, "%Y-%m-%d"
            ).date()
            cards = cards.filter(
                issue_date__year=issue_date.year,
                issue_date__month=issue_date.month,
                issue_date__day=issue_date.day,
            )

        if expire_date_text:
            expire_date = datetime.datetime.strptime(
                expire_date_text, "%Y-%m-%d"
            ).date()
            cards = cards.filter(
                expire_date__year=expire_date.year,
                expire_date__month=expire_date.month,
                expire_date__day=expire_date.day,
            )

        if status != CardSearchForm.ANY:
            cards = cards.filter(status=status)

        return cards

    def get_context_data(self, **kwargs):
        context = super(CardListView, self).get_context_data(**kwargs)
        context['form'] = CardSearchForm()
        return context


class CardDetailView(generic.DetailView):
    """Отображает информацию о Карте."""
    template_name = 'cards/card_info.html'
    model = Card
    pk_url_kwarg = 'card_id'


def card_activate(request, card_id):
    """Активация Карты."""
    template = 'cards/card_activate.html'
    card = get_object_or_404(Card, id=card_id)
    card.activate()
    card.save()
    context = {'card': card}
    return render(request, template, context)


def card_deactivate(request, card_id):
    """Деактивация Карты."""
    template = 'cards/card_deactivate.html'
    card = get_object_or_404(Card, id=card_id)
    card.deactivate()
    card.save()
    context = {'card': card}
    return render(request, template, context)


def card_delete(request, card_id):
    """Удаление Карты."""
    template = 'cards/card_delete.html'
    card = get_object_or_404(Card, id=card_id)
    context = {'card': card}
    card.delete()
    return render(request, template, context)


def card_generator(request):
    """Генератор Карт."""
    template = 'cards/card_generator.html'
    form = CardGeneratorForm()
    context = {'form': form}

    if request.method == 'POST':
        generator_input_info = CardGeneratorForm(request.POST)
        if generator_input_info.is_valid():
            series = generator_input_info.cleaned_data['series']
            quantity = generator_input_info.cleaned_data['quantity']
            duration = generator_input_info.cleaned_data['duration']
            issue_datetime = timezone.now()
            expire_datetime = issue_datetime + relativedelta(months=duration)
            current_sum = 0

            # Находим все имеющиеся карточки данной серии и вычисляем сколько
            # номеров свободно для новых карт между данной картой и предыдущей
            current_cards = Card.objects.filter(series=series).annotate(
                previous_card_number=Window(
                    expression=Lag(expression='number', default=0),
                    order_by='number',
                )
            ).annotate(
                free_slots_before=(
                    F('number') - F('previous_card_number') - 1
                )
            )
            prepared_numbers = []
            prepared_numbers_quantity = 0

            # В первую очередь исползуем номера между действующими картами
            for card in current_cards:
                if prepared_numbers_quantity < quantity:
                    if card.free_slots_before > 0:
                        left_to_make = quantity - prepared_numbers_quantity
                        cards_to_make = min(
                            left_to_make, card.free_slots_before
                        )
                        for lag in range(1, cards_to_make+1):
                            prepared_numbers.append(
                                card.previous_card_number+lag
                            )
                            prepared_numbers_quantity += 1
                else:
                    break

            if prepared_numbers_quantity < quantity:
                if current_cards:
                    prepared_numbers.append(current_cards.last().number+1)
                    prepared_numbers_quantity += 1
                else:
                    prepared_numbers.append(1)
                    prepared_numbers_quantity += 1

            while prepared_numbers_quantity < quantity:
                prepared_numbers.append(prepared_numbers[-1]+1)
                prepared_numbers_quantity += 1

            objects = [
                Card(
                    series=series, issue_date=issue_datetime,
                    expire_date=expire_datetime, number=number,
                    current_sum=current_sum,
                ) for number in prepared_numbers
            ]
            Card.objects.bulk_create(objects)
            return redirect('cards:card_list')
        else:
            context['form'] = generator_input_info
            return render(request, template, context)
    return render(request, template, context)
