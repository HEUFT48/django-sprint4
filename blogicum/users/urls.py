from django.urls import path

from blog import views

app_name = 'users'

urlpatterns = [
    path('auth/registration/',
         views.RegistrationView.as_view(),
         name='registration'),
    path('profile/<str:username>/',
         views.UserProfileView.as_view(),
         name='profile'),
    path('profile/<str:username>/edit/',
         views.ProfileEditView.as_view(),
         name='edit_profile'),
]
