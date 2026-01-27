from django.urls import path

from . import views


app_name = 'blog'


urlpatterns = [
    path('posts/<int:id>/',
         views.post_detail,
         name='post_detail'),
    path('', views.index, name='index'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'),
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('posts/<int:pk>/edit/',
         views.PostEditView.as_view(),
         name='edit_post'),
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),
    path('profile/<str:username>/',
         views.profile, name='profile'),
    path('posts/<int:post_id>/edit_comment/<int:pk>/',
         views.CommentEditView.as_view(),
         name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:pk>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
    path('posts/<int:post_id>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
]
