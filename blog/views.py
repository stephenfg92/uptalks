from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, FormView, FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import RedirectView
from django.contrib.auth import get_user_model
from django.views.generic.edit import UpdateView, CreateView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django_registration.backends.one_step.views import RegistrationView
from django.views.generic import ListView

from .models import UserProfile, Post, Vote, Comment

from .forms import UserProfileForm, PostForm, VoteForm, CommentForm

#Imports para viabilizar uso do Django Rest Framework
from .serializers import PostSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication, permissions

from django.core.paginator import Paginator

from django.db.models import Count

import json

class post_list(LoginRequiredMixin ,ListView): 
	login_url = 'login'
	redirect_field_name = 'redirect_to'
	context_object_name = 'posts'
	template_name = 'blog/post/list.html'
	paginate_by = 10

	'''
	def dispatch(self, request, *args, **kwargs):
		if not self.request.user.is_authenticated:
			return redirect('login')
	'''

	def get_context_data(self, **kwargs):
		context = super(post_list, self).get_context_data(**kwargs)
		voted = Vote.objects.all().filter(voter=self.request.user)
		posts_in_page = [post.id for post in context["object_list"]]
		voted = voted.filter(post_id__in=posts_in_page)
		voted = voted.values_list("post_id", flat=True)
		context["voted"] = voted
		return context

	def get_queryset(self, *args, **kwargs):
		#qs = Post.with_votes.all()
		qs = Post.with_votes.all().annotate(comment_count=Count('comments'))
		query = self.request.GET.get('q', None)
		if query:
			qs = qs.filter(
				Q(title__icontains=query) |
				Q(user__username__icontains=query)
			)
		return qs

#É por aqui que o aplicativo android irá adquirir os posts publicados
@api_view(['get'])
def fetch_posts(request):
	posts = Post.with_votes.all()
	serializer = PostSerializer(posts, many=True)
	return Response(serializer.data)

class post_detail(FormMixin, DetailView):
	model = Post
	template_name = 'blog/post/detail.html'
	form_class = CommentForm

	def get_success_url(self):
		return reverse('blog:post_detail', kwargs={'slug': self.object.slug})

	def get_context_data(self, **kwargs):
		context = super(post_detail, self).get_context_data(**kwargs)

		#Dados de contexto para publicação de comentários
		if self.object.status == 'anonym' and self.request.user == self.object.author:
			context['form'] = CommentForm(initial={'author': 'Autor da publicação', 'post': self.object})
		else:
			context['form'] = CommentForm(initial={'author': self.request.user.userprofile, 'post': self.object})

		#Dados de contexto para identificaçãoi de posts votados pelo usuário atual
		if Vote.objects.all().filter(voter=self.request.user, post=self.object):
			voted = True
			context["voted"] = voted

		return context

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def form_valid(self, form):
		form.save()
		return super(post_detail, self).form_valid(form)

#Detalhes do usuário
class UserProfileDetailView(DetailView):
	model = get_user_model()
	slug_field = 'username'
	template_name = 'user_detail.html'

	def get_object(self, queryset = None):
		user = super(UserProfileDetailView, self).get_object(queryset)
		if self.request.user.username == user.username:
			UserProfile.objects.get_or_create(user=user)
			return user
		else:
			return redirect('login')


#Editar perfil
class UserProfileEditView(UpdateView):
	model = UserProfile
	form_class = UserProfileForm
	template_name = 'edit_profile.html'

	def get_object(self, queryset=None):
		instance = UserProfile.objects.get_or_create(user=self.request.user)
		return instance[0]

	def get_success_url(self):
		#return reverse('profile', kwargs={'slug': self.request.user})
		return reverse_lazy('blog:post_list')

#Submeter post
class PostCreateView(CreateView):
	model = Post
	form_class = PostForm

	def form_valid(self, form):
		form.instance.author = self.request.user
		form.instance.rank_score = 0.0
		return super().form_valid(form)

#Atualizar post
class PostUpdateView(UpdateView):
	model = Post
	form_class = PostForm
	
	def get_absolute_url(self):
		return reverse('blog:post_update', kwargs={'slug': self.slug})

#Excluir post
class PostDeleteView(DeleteView):
	model = Post
	success_url = reverse_lazy('blog:post_list')

	def post(self, request, *args, **kwargs):
		if "cancel" in request.POST:
			return HttpResponseRedirect(reverse_lazy('blog:post_detail', kwargs={'slug': self.kwargs['slug']}))
		else:
			return super(PostDeleteView, self).post(request, *args, **kwargs)

class VoteView(RedirectView):

	def get(self, request, *args, **kwargs):
		slug = self.kwargs['slug']
		user = self.request.user
		post = get_object_or_404(Post, slug=slug)

		#Checa se já houve voto
		prev_votes = Vote.objects.filter(voter=user, post=post)
		has_voted = (prev_votes.count() > 0)

		if user.is_authenticated:
			if not has_voted:
				post.score = post.score + 1
				Vote.objects.create(voter=user, post=post)
				post.save()
				return redirect(request.META.get('HTTP_REFERER', 'blog:post_list'))
			else:
				prev_votes[0].delete()
				post.score = post.score - 1
				post.save()
				return redirect(request.META.get('HTTP_REFERER', 'blog:post_list'))
		return redirect('login')

class VoteAPIView(APIView):

	authentication_classes = (authentication.SessionAuthentication,)
	permission_classes = (permissions.IsAuthenticated,)

	def get(self, request, slug=None, format=None):
		user = self.request.user
		post = get_object_or_404(Post, slug=slug)
		updated = False
		voted = False

		#Checa se já houve voto
		prev_votes = Vote.objects.filter(voter=user, post=post)
		has_voted = (prev_votes.count() > 0)

		if user.is_authenticated:
			if not has_voted:
				post.score = post.score + 1
				Vote.objects.create(voter=user, post=post)
				post.save()
				voted = True
			else:
				prev_votes[0].delete()
				post.score = post.score - 1
				post.save()
				voted = False
			updated = True

		data = {
			"updated": updated,
			"voted": voted,
			"count": post.score
		}
		return Response(data)