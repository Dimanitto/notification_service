import logging

from django.contrib.auth.views import LoginView
from django_celery_beat.models import PeriodicTask
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from mailing import models, serializers
from mailing.datatools.mailing_tasks import process_mailing
from mailing.datatools.message_statistics import get_message_statistics

logger = logging.getLogger('django')


class CustomLoginView(LoginView):
    """Изменен базовый шаблон входа, для авторизации через google account"""
    template_name = 'mailing/admin/custom_login.html'


class MailingViewSet(viewsets.ModelViewSet):
    queryset = models.Mailing.objects.all()
    serializer_class = serializers.Mailing

    def perform_destroy(self, instance: models.Mailing) -> None:
        """
        При удалении рассылки, будут удалены все запланированные задачи
        """
        PeriodicTask.objects.filter(args=f'[{instance.id}]').delete()
        logger.info(f'Рассылка: {instance.id} удалена.')
        instance.delete()

    def perform_update(self, serializer: serializers.Mailing) -> None:
        """
        При изменении рассылки старые задачи будут удалены и созданы новые
        """
        mailing = serializer.save()
        PeriodicTask.objects.filter(args=f'[{mailing.id}]').delete()
        process_mailing(mailing)
        logger.info(f'Рассылка: {mailing.id} изменена.')

    @action(
        detail=True, methods=['get'],
        serializer_class=serializers.MailingStatistic
    )
    def statistic(self, request: Request, pk: int) -> Response:
        mailing = self.get_object()
        data = get_message_statistics(mailing)
        serializer = self.serializer_class(data[0])
        return Response(serializer.data)

    @action(
        detail=False, methods=['get'],
        serializer_class=serializers.MailingStatistic
    )
    def statistics(self, request: Request) -> Response:
        data = get_message_statistics()
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = models.Client.objects.all()
    serializer_class = serializers.Client

    def perform_create(self, serializer: serializers.Client) -> None:
        client = serializer.save()
        logger.info(f'Клиент: {client.id} создан.')

    def perform_update(self, serializer: serializers.Client) -> None:
        client = serializer.save()
        logger.info(f'Клиент: {client.id} изменен.')

    def perform_destroy(self, instance: models.Client) -> None:
        logger.info(f'Клиент: {instance.id} удален.')
        instance.delete()


class MobileOperatorViewSet(viewsets.ModelViewSet):
    queryset = models.MobileOperator.objects.all()
    serializer_class = serializers.MobileOperator


class TagViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.Tag
