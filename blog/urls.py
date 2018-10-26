from django.conf.urls import url
from django.urls import include, path
from . import views
from django.contrib.auth.views import LoginView, logout_then_login
from django.contrib.auth.decorators import login_required as auth

from django.views.decorators.cache import never_cache

app_name='blog'
urlpatterns = [
    #post views
    path('', views.post_list.as_view(), name='post_list'),
    path('<slug:slug>/', views.post_detail.as_view(), name='post_detail'),
    path('update/<slug:slug>/', auth(views.PostUpdateView.as_view()), name='post_update'),
    path('delete/<slug:slug>/', auth(views.PostDeleteView.as_view()), name='post_delete'),
    path('api/vote/<slug:slug>/', auth(views.VoteAPIView.as_view()), name='post_api_vote'),
    path('poll/<int:pk>/', auth(views.PollDetail.as_view()), name='poll_detail'),
    path('poll/<int:pk>/results', auth(views.PollResults.as_view()), name='poll_results'),
    path('poll/<int:question_id>/vote', auth(views.poll_vote), name='poll_vote'),
    url(r'fetch', views.fetch_posts, name='fetch_posts'),
    url(r'create', auth(views.PostCreateView.as_view()), name='post_create')
]