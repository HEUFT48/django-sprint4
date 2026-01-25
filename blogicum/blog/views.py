from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib import messages
from django import forms
from .models import Post, Category, Comment
from django.contrib.auth import get_user_model

from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


# КЛАСС ДЛЯ РЕДАКТИРОВАНИЯ ПРОФИЛЯ
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'password': forms.HiddenInput(),
        }


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('blog:profile', username=request.user.username)
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})


def home(request):
    """Главная страница сайта"""
    return index(request)


def index(request):
    print(
        f"DEBUG: User: {request.user}, "
        f"authenticated: {request.user.is_authenticated}"
    )

    posts = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        Q(is_published=True),
        Q(category__is_published=True),
        Q(pub_date__lte=timezone.now())
    ).order_by('-pub_date')

    print(f"DEBUG: Found {posts.count()} posts")

    posts = posts.annotate(comment_count=Count('comments'))

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    class SimpleCommentForm(forms.Form):
        text = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    context = {
        'page_obj': page_obj,
        'form': SimpleCommentForm(),
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        id=id
    )

    if not post.is_published and request.user != post.author:
        raise Http404("Пост не найден")

    if not post.category.is_published and request.user != post.author:
        raise Http404("Категория не найдена")

    if post.pub_date > timezone.now() and request.user != post.author:
        raise Http404("Пост еще не опубликован")

    comments = post.comments.select_related('author').all()

    class SimpleCommentForm(forms.Form):
        text = forms.CharField(
            widget=forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Введите комментарий'})
        )

    post_with_counts = Post.objects.filter(
        id=post.id).annotate(comment_count=Count('comments')).first()

    context = {
        'post': post_with_counts or post,
        'form': SimpleCommentForm(),
        'comments': comments,
        'is_post_author': request.user == post.author,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    posts = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        Q(category=category),
        Q(is_published=True),
        Q(pub_date__lte=timezone.now())
    ).order_by('-pub_date')

    posts = posts.annotate(comment_count=Count('comments'))

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    class SimpleCommentForm(forms.Form):
        text = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    context = {
        'category': category,
        'page_obj': page_obj,
        'form': SimpleCommentForm(),
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    is_owner = request.user == user

    if is_owner:
        posts = user.posts.select_related('category',
                                          'location',
                                          'author').all()
    else:
        posts = user.posts.select_related('category',
                                          'location',
                                          'author').filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    posts = posts.annotate(comment_count=Count('comments')
                           ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    class SimpleCommentForm(forms.Form):
        text = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    context = {
        'profile': user,
        'profile_user': user,
        'page_obj': page_obj,
        'first_name': user.first_name,
        'is_owner': is_owner,
        'form': SimpleCommentForm(),
    }
    return render(request, 'blog/profile.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    fields = ['title', 'text', 'image', 'category', 'location', 'pub_date']

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Пост успешно создан!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    fields = ['title', 'text', 'image', 'category', 'location', 'pub_date']

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('blog:post_detail', id=self.kwargs.get('pk'))

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'id': self.object.id})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('blog:post_detail', id=self.kwargs.get('pk'))

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class CommentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ['text']
    template_name = 'blog/comment.html'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        comment = self.get_object()
        return redirect('blog:post_detail', id=comment.post.id)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'id': self.object.post.id})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['text']
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        messages.success(self.request, 'Комментарий добавлен!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'id': self.kwargs['post_id']})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.get_object()
        return context

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        comment = self.get_object()
        return redirect('blog:post_detail', id=comment.post.id)

    def get_success_url(self):
        post_id = self.kwargs.get('post_id') or self.object.post.id
        return reverse_lazy('blog:post_detail', kwargs={'id': post_id})
