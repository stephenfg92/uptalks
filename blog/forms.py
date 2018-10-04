from django.forms import ModelForm, Textarea, HiddenInput
from .models import UserProfile, Post, Comment

#Form para edição de perfil
class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        #exclude = ('user', ) -> Sintaxe antiga
        exclude = ['user']
        #Ao invés de exlude, é possível usar a variável fields = ['campo1', 'campo2', ...
        labels = {'ultimo_nome': 'Último nome'}

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'status']
        labels = {'title': ('Título'), 'body': ('Texto'), 'status': ('Modo de publicação:'),}
        widgets = {
            'body': Textarea(attrs={'cols': 29, 'rows': 10}),
        }

class VoteForm(ModelForm):
    class Meta:
        model = Post
        fields = ('slug', 'author', 'score')

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'text', 'post',)
        labels = {'text': ''}
        widgets = {
            'author': HiddenInput(),
            'post': HiddenInput(),
        }