from django.urls import path, include
from .views import (
    print_photo,
)

urlpatterns = [
    path('api/print', print_photo, name='print_photo'),
]