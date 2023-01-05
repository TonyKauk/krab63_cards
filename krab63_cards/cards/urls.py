from django.urls import path

from . import views

app_name = 'cards'


urlpatterns = [
    path('', views.CardListView.as_view(), name='card_list'),
    path('<int:card_id>/', views.CardDetailView.as_view(), name='card_info'),
    path(
        '<int:card_id>/activate/', views.card_activate,
        name='card_activate',
    ),
    path(
        '<int:card_id>/deactivate/', views.card_deactivate,
        name='card_deactivate',
    ),
    path(
        '<int:card_id>/delete/', views.card_delete,
        name='card_delete',
    ),
    path(
        'generator/', views.card_generator,
        name='card_generator',
    ),
]
