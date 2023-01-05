from django.contrib import admin

# from .forms import QuestionAdminForm
from .models import Card, Operation


# class QuestionAdmin(admin.ModelAdmin):
#     form = QuestionAdminForm
#     pass


admin.site.register(Card)
admin.site.register(Operation)
