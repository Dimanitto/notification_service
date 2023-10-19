from django.urls import path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter

from mailing import views

app_name = 'mailing'

urlpatterns = [
    path('', RedirectView.as_view(url='/backend/docs/')),
    path(
        'admin/login/',
        views.CustomLoginView.as_view(),
        name='custom_admin_login'
    ),
]

router = DefaultRouter()
router.register('mailings', views.MailingViewSet, basename='mailings')
router.register('clients', views.ClientViewSet, basename='clients')
router.register(
    'mobile_operators', views.MobileOperatorViewSet,
    basename='mobile_operators'
)
router.register('tags', views.TagViewSet, basename='tags')

urlpatterns += router.urls
