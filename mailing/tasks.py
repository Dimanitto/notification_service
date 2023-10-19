import logging
from datetime import datetime, timedelta

import pytz
import requests
from constance import config
from django.core.mail import send_mail
from django.db.models import Q, Count

from mailing import models, conts
from notification import celery_app, settings

RETRY_SECONDS = 6 * 60

logger = logging.getLogger('tasks')


@celery_app.task
def distribution_mailing(mailing_id: int) -> None:
    """Формирование рассылки"""
    logger.info(f'Начинается рассылка с id {mailing_id}')
    mailing = models.Mailing.objects.get(id=mailing_id)
    q = Q()
    # Выбираем клиентов подходящих либо под код оператора либо по тегу
    if operators := mailing.operators.all():
        q = q | Q(operator__in=operators)
    if tags := mailing.tags.all():
        q = q | Q(tag__in=tags)
    # Если в рассылке не были указаны теги и код оператора,
    # рассылка распространяется на всех клиентов
    clients = models.Client.objects.filter(q)
    for client in clients:
        # Учтем часовой пояс клиента, узнаем его локальное время
        client_timezone = pytz.timezone(client.timezone)
        client_datetime = datetime.now(client_timezone)
        mailing_datetime = datetime.combine(
            datetime.today(),
            mailing.time_start
        )
        if mailing.time_start <= client_datetime.time() <= mailing.time_end:
            send_one_notify.delay(
                mailing.id, client.id, client.phone,
                mailing.text, mailing.time_end, client.timezone
            )
        elif client_datetime.time() <= mailing.time_start:
            datetime_difference = (mailing_datetime -
                                   client_datetime.replace(tzinfo=None))
            send_one_notify.apply_async(
                args=(
                    mailing.id, client.id, client.phone,
                    mailing.text, mailing.time_end, client.timezone
                ),
                countdown=datetime_difference.total_seconds()
            )


@celery_app.task(max_retries=10)
def send_one_notify(
        mailing_id: int, client_id: int, phone: str, text: str,
        time_end: datetime.time, client_timezone: str, message_id: int = None,
) -> None:
    """
    Отправка сообщения на сторонний сервис.
    В случае неудачного ответа сервиса, будут применены:
    10 попыток в течение часа с интервалом 6 минут или
    если время рассылки вышло.
    """
    client_timezone = pytz.timezone(client_timezone)
    now_time = datetime.now(client_timezone).time()
    if now_time >= time_end:
        return
    if not message_id:
        message = models.Message.objects.create(
            client_id=client_id,
            mailing_id=mailing_id,
        )
        message_id = message.id
    try:
        logger.info(f'Отправка сообщения {message_id} рассылки {mailing_id} '
                    f'клиенту с номером {phone}.')
        response = requests.post(
            url=config.API_SERVICE_URL + str(message_id),
            headers={'Authorization': f'Bearer {config.API_SERVICE_TOKEN}'},
            json={
                'id': message_id,
                'phone': phone,
                'text': text,
            },
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        retries = send_one_notify.request.retries
        max_retries = send_one_notify.max_retries
        logger.warning(f'Сообщение {message_id} рассылки {mailing_id} клиенту '
                       f'{phone} не было отправлено. Ошибка {e}, '
                       f'попытка {retries}/{max_retries}')
        send_one_notify.retry(
            exc=e, countdown=RETRY_SECONDS, kwargs={'message_id': message_id}
        )
    else:
        if response.status_code == requests.codes.ok:
            message = models.Message.objects.get(id=message_id)
            message.status = conts.STATUS_SENT
            message.save(update_fields=['status'])
            logger.info(f'Сообщение клиенту {phone} успешно отправлено.')


@celery_app.task
def send_daily_stats_email():
    """
    Раз в сутки отправляем статистику по рассылкам на email
    """
    yesterday_date = datetime.now() - timedelta(days=1)
    messages = models.Message.objects.filter(
        dc__gte=yesterday_date
    ).values(
        'status'
    ).annotate(
        count=Count('status')
    )
    message_stats = "Статистика по сообщениям за прошедшие сутки:\n"
    for message in messages:
        status, count = message.values()
        message_stats += f'Статус {status}: {count}\n'
    recipient_list = config.RECIPIENT_LIST_EMAILS.split(', ')
    send_mail(
        subject='Статистика по сообщениям',
        message=message_stats,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )
