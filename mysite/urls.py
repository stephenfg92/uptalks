from django.urls import path, include
from django.contrib import admin
from blog.views import UserProfileDetailView, UserProfileEditView
from django_registration.views import RegistrationView
from django.contrib.auth.decorators import login_required as auth
from django.conf import settings
from django.conf.urls.static import static
from django_registration.backends.one_step.views import RegistrationView
from django.urls import reverse_lazy

from django.views.generic import TemplateView

from django.views.decorators.cache import never_cache


urlpatterns = [
    path('admin/', admin.site.urls),
    #path('service-worker.js', cache_control(max_age=2592000)(TemplateView.as_view(
    #template_name="service-worker.js",
    #content_type='application/javascript',
#)), name='service-worker.js'),
    path('service-worker.js', never_cache((TemplateView.as_view(
        template_name="service-worker.js",
        content_type='application/javascript',
        ))), name='service-worker.js'),
    path('', include('blog.urls', namespace='blog')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/register', RegistrationView.as_view(success_url=reverse_lazy('edit_profile')), name='django_registration_register'),
    path('users/<slug:slug>/', UserProfileDetailView.as_view(), name="profile"),
    path('accounts/edit_profile/', auth(UserProfileEditView.as_view()), name='edit_profile'),
    path('comments/', include('django_comments.urls'))
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
