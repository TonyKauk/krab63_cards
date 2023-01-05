from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.utils import timezone
from django.db.models import RowRange, Window, F, Sum
from django.db.models.functions import Lag, FirstValue, LastValue, Lead

from .forms import CardGeneratorForm
from .models import Card


class CardListView(generic.ListView):
    """Отображает все Карты."""
    template_name = 'cards/card_list.html'
    context_object_name = 'cards'
    model = Card


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
    """Деактивация Карты."""
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
        series = generator_input_info['series']
        quantity = generator_input_info['quantity']
        duration = generator_input_info['duration']
        issue_datetime = datetime.now()
        expire_datetime = issue_datetime + relativedelta(months=duration)
        current_sum = 0

        current_cards = Card.objects.filter(series=series).annotate(
            previous_card_number=Window(
                expression=Lag(expression='number', default=0),
                order_by='number',
            )
        ).annotate(
            free_slots_before=(F('number') - F('previous_card_number') - 1)
        )

        prepared_numbers = []
        prepared_numbers_quantity = 0

        for card in current_cards:
            if prepared_numbers_quantity < quantity:
                if card.free_slots_before > 0:
                    left_to_make = quantity - prepared_numbers_quantity
                    cards_to_make = min(left_to_make, card.free_slots_before)
                    for lag in range(1, cards_to_make+1):
                        prepared_numbers.append(card.previous_card_number+lag)
                        prepared_numbers_quantity += 1
            else:
                break

        if prepared_numbers_quantity < quantity:
            prepared_numbers.append(current_cards.last().number+1)
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
##############################################################################
    # template = 'cards/card_list_gen.html'
    # series = 1
    # current_cards = Card.objects.filter(series=series).annotate(
    #     previous_card_number=Window(
    #         expression=Lag(expression='number', default=0),
    #         order_by='number',
    #     )
    # ).annotate(
    #     free_slots_before=(F('number') - F('previous_card_number') - 1)
    # )

    # quantity = 25

    # prepared_numbers = []
    # prepared_numbers_quantity = 0

    # for card in current_cards:
    #     if prepared_numbers_quantity < quantity:
    #         if card.free_slots_before > 0:
    #             left_to_make = quantity - prepared_numbers_quantity
    #             cards_to_make = min(left_to_make, card.free_slots_before)
    #             for lag in range(1, cards_to_make+1):
    #                 prepared_numbers.append(card.previous_card_number+lag)
    #                 prepared_numbers_quantity += 1
    #     else:
    #         break

    # if prepared_numbers_quantity < quantity:
    #     prepared_numbers.append(current_cards.last().number+1)
    #     prepared_numbers_quantity += 1

    # while prepared_numbers_quantity < quantity:
    #     prepared_numbers.append(prepared_numbers[-1]+1)
    #     prepared_numbers_quantity += 1

    # context = {
    #     'current_cards': current_cards,
    #     'prepared_numbers': prepared_numbers,
    # }
    # return render(request, template, context)
