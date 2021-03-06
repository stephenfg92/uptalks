from django.contrib import admin
from .models import Post, UserProfile, Vote, Comment, Question, Choice, PollVote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status', 'score', 'rank')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']

admin.site.register(Post, PostAdmin)

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['title', 'author', 'rank', 'score','question_text']}),
        ('Date information', {'fields': ['publish'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]

admin.site.register(Question, QuestionAdmin)

class PollVoteAdmin(admin.ModelAdmin): pass
admin.site.register(PollVote, PollVoteAdmin)

admin.site.register(Comment)

class VoteAdmin(admin.ModelAdmin): pass

admin.site.register(Vote, VoteAdmin)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserProfileAdmin(UserAdmin):
    inlines = (UserProfileInline, )

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserProfileAdmin)