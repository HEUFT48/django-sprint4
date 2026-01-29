from django.urls import path
from django.views.generic import RedirectView, TemplateView

from .views import ProfileEditView

app_name = 'pages'

urlpatterns = [

    path('about/',
         TemplateView.as_view(template_name='pages/about.html'),
         name='about'),
    path('rules/',
         TemplateView.as_view(template_name='pages/rules.html'),
         name='rules'),
    path('profile/<str:username>/',
         RedirectView.as_view(pattern_name='blog:profile', permanent=False),
         name='profile'),
    path('profile/<str:username>/edit/',
         ProfileEditView.as_view(),
         name='edit_profile'),
]
