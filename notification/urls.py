from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from notification import settings

schema_view = get_schema_view(
    openapi.Info(
        title='Notification API',
        default_version='v1',
        description='Сервис управления рассылками',
        contact=openapi.Contact(url='https://t.me/dimanitto'),
    ),
    permission_classes=[AllowAny]
)

urlpatterns = [
    path('', RedirectView.as_view(url='/backend/')),
    path('backend/', include('mailing.urls', namespace='mailing')),
    path('backend/admin/', admin.site.urls),
    path(
        'backend/docs/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'backend/social-auth/',
        include('social_django.urls', namespace='social')
    ),

]

if settings.DEBUG:
    urlpatterns += static('backend/media', document_root=settings.MEDIA_ROOT)
