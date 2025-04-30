from django.urls import path, include
from views import UserLoginView

urlpatterns = [
    path('login/', UserLoginView.as_view()),
]