# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

# from quizes.forms import QuestionResultForm
from .models import Card


class CardListView(generic.ListView):
    """Отображает все Карты."""
    template_name = 'cards/cards_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.all()
