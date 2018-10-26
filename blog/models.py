from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now
from .utils import get_unique_slug
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save
from django.core.validators import RegexValidator

class VoteManager(models.Manager):
	def get_queryset(self):
		return super(VoteManager, self).get_queryset().order_by('-rank', '-score')

class Post(models.Model):
	STATUS_CHOICES = (('anonym', 'Anônimo'), ('public', 'Identificado'))
	title = models.CharField(max_length=250)
	slug  = models.SlugField(blank=True, unique=True, max_length=250)
	author = models.ForeignKey(User, related_name='blog_posts', on_delete=models.CASCADE, max_length=250)
	body = models.TextField(max_length=5000)
	publish = models.DateTimeField(default=timezone.now)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='public')
	score = models.IntegerField(default=1)
	rank = models.FloatField(default=0.0)

	objects = models.Manager() #Model manager default
	with_votes = VoteManager() # Manager Custom para encontrar posts publicados e com votos

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = get_unique_slug(self, 'title', 'slug')
		super().save(*args, **kwargs)

	#Ao trabalhar apenas com slug, use kwargs ao invés de args. Sei lá pq.
	def get_absolute_url(self):
		return reverse('blog:post_detail', kwargs={'slug': self.slug})


	def get_api_vote_url(self):
		return reverse("blog:post_api_vote", kwargs={"slug": self.slug})

	def age(self):
		t = ((timezone.now()-self.created).total_seconds())
		if t > 86400:
			return "{} dias".format("%.0f" % (t / 86400))
		elif t < 3600:
			return "{} minutos".format("%.0f" % (t / 60))
		elif t > 3600:
			return "{} horas".format("%.0f" % (t / 3600))

	def set_rank(self):
		SECS_IN_HOUR = float(60*60)
		GRAVITY = 1.2

		delta = now() - self.created
		print(delta)
		item_hour_age = delta.total_seconds() // SECS_IN_HOUR
		votes = self.score - 1
		self.rank = votes / pow((item_hour_age + 2), GRAVITY)
		self.save()

	class Meta:
		ordering = ('-publish',)

	def __str__(self):
		return self.title

	def postOrVote(self):
		return 'post'

class Vote(models.Model):
	voter = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)

	def __str__(self):
		return self.voter.username + ' upvoted ' + self.post.title


class UserProfile(models.Model):
	user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
	primeiro_nome = models.CharField(default='', max_length=50)
	ultimo_nome = models.CharField(default='', max_length=50)
	cpf = models.CharField(default='Apenas números', max_length=16, validators=[RegexValidator(r'([0-9]{2}[\.]?[0-9]{3}[\.]?[0-9]{3}[\/]?[0-9]{4}[-]?[0-9]{2})|([0-9]{3}[\.]?[0-9]{3}[\.]?[0-9]{3}[-]?[0-9]{2})')])
	apartamento = models.CharField(default='Apto', max_length=10, validators=[RegexValidator(r'^\d{1,10}$')])

	def __str__(self):
		return self.primeiro_nome + ' ' + self.ultimo_nome

	def create_profile(sender, instance, created, **kwargs):
		if created:
			profile, created =  UserProfile.objects.get_or_create(user=instance)


	#Sinaliza gravação de usuário
	post_save.connect(create_profile, sender=User)

class Comment(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
	author = models.CharField(max_length=200)
	text = models.TextField(max_length=9999)
	created = models.DateTimeField(auto_now_add=True)
	approved = models.BooleanField(default=True)

	def hide(self):
		self.approved_comment = False
		self.save()

	def age(self):
		t = ((timezone.now()-self.created).total_seconds())
		if t > 86400:
			return "{} dias".format("%.0f" % (t / 86400))
		elif t < 3600:
			return "{} minutos".format("%.0f" % (t / 60))
		elif t > 3600:
			return "{} horas".format("%.0f" % (t / 3600))

	def __str__(self):
		return self.text

#Surveys

class Question(models.Model):
	question_text = models.TextField(max_length=1000)
	publish = models.DateTimeField(default=timezone.now)
	STATUS_CHOICES = (('hidden', 'Oculto'), ('public', 'Público'))
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='public')

	#Campos necessários para integração com view post_list
	title = models.CharField(max_length=250)
	author = models.ForeignKey(User, related_name='question', on_delete=models.CASCADE, max_length=250)
	score = models.IntegerField(default=0)
	rank = models.FloatField(default=100)

	with_votes = VoteManager()

	def age(self):
		t = ((timezone.now()-self.publish).total_seconds())
		if t > 86400:
			return "{} dias".format("%.0f" % (t / 86400))
		elif t < 3600:
			return "{} minutos".format("%.0f" % (t / 60))
		elif t > 3600:
			return "{} horas".format("%.0f" % (t / 3600))

	def get_absolute_url(self):
		return reverse('blog:poll_detail', kwargs={'pk': self.pk})

	def __str__(self):
		return self.question_text

class Choice(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	choice_text = models.CharField(max_length=200)
	votes = models.IntegerField(default=0)

	def __str__(self):
		return self.choice_text

	def postOrVote(self):
		return 'vote'

class PollVote(models.Model):
	voter = models.ForeignKey(User, on_delete=models.CASCADE)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	choice = models.CharField(max_length=200)

	def __str__(self):
		return self.voter.username + ' voted on ' + self.question.question_text + ' at option ' + self.choice 