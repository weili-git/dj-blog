from django.urls import path, include

from . import views

urlpatterns = [
    path('post', views.PostIndexView.as_view(), name='post index'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post detail'),
    path('post/create', views.PostCreateForm.as_view(), name='post create'),
    path('post/update/<int:pk>/', views.PostUpdateView.as_view(), name='post create'),
    path('post/delete/<int:pk>/', views.PostDeleteView.as_view(), name='post delete'),

    path('category', views.CategoryIndexView.as_view(), name='category index'),
    path('category/<int:pk>/', views.CategoryDetailView.as_view(), name='category detail'),
    path('category/create', views.CategoryCreateView.as_view(), name='category create'),
    path('category/delete/<int:pk>/', views.CategoryDeleteView.as_view(), name='category delete'),

    path('search', views.search_view, name='search')
]