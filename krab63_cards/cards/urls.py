from django.urls import path

from . import views

app_name = 'cards'


urlpatterns = [
    path('', views.CardListView.as_view(), name='cards_list'),
    # path('<int:quiz_id>/welcome/', views.quiz_welcome, name='quiz_welcome'),
    # path(
    #     '<int:quiz_id>/<int:question_id>',
    #     views.quiz_question, name='quiz_question',
    # ),
    # path(
    #     '<int:quiz_id>/results/',
    #     views.quiz_results, name='quiz_results',
    # ),
]
