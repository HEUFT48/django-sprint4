from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.views.generic import View
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from blog.models import Post
from .utils import paginate_page


def home(request):
    posts_list = Post.objects.filter(is_published=True).order_by('-pub_date')
    page_obj = paginate_page(request, posts_list, posts_per_page=10)
    return render(request, 'pages/home.html', {'page_obj': page_obj})


@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        posts_list = Post.objects.filter(
            author=profile_user
        ).order_by('-pub_date')
    else:
        posts_list = Post.objects.filter(
            author=profile_user,
            is_published=True
        ).order_by('-pub_date')

    page_obj = paginate_page(request, posts_list, posts_per_page=10)

    context = {
        'profile_user': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'pages/profile.html', context)


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    template_name = 'pages/profile_edit.html'
    fields = ['first_name', 'last_name', 'username', 'email']
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user


def about(request):
    return render(request, 'pages/about.html')


def rules(request):
    return render(request, 'pages/rules.html')


class AboutView(View):
    template_name = 'pages/about.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class RulesView(View):
    template_name = 'pages/rules.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    return render(request, 'pages/500.html', status=500)
