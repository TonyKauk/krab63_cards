from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('cards.urls', namespace='cards')),
    path('admin/', admin.site.urls),
]
