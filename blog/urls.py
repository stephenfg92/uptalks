from django.conf.urls import url
from django.urls import include, path
from . import views
from django.contrib.auth.views import LoginView, logout_then_login
from django.contrib.auth.decorators import login_required as auth

app_name='blog'
urlpatterns = [
    #post views
    path('', views.post_list.as_view(), name='post_list'),
    path('<slug:slug>/', views.post_detail.as_view(), name='post_detail'),
    path('update/<slug:slug>/', auth(views.PostUpdateView.as_view()), name='post_update'),
    path('delete/<slug:slug>/', auth(views.PostDeleteView.as_view()), name='post_delete'),
    path('vote/<slug:slug>/', auth(views.VoteView.as_view()), name='post_vote'),
    path('api/vote/<slug:slug>/', auth(views.VoteAPIView.as_view()), name='post_api_vote'),
    url(r'fetch', views.fetch_posts, name='fetch_posts'),
    url(r'create', auth(views.PostCreateView.as_view()), name='post_create')
]