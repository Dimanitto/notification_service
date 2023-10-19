from datetime import datetime, timedelta

from constance import config
from django_celery_beat.models import ClockedSchedule, PeriodicTask

from mailing import models
from notification.celery import app


def process_mailing(mailing: models.Mailing) -> None:
    """
    Создаем задачи по рассылкам, каждый день - отдельная задача,
    которая будет вызывать формирование рассылки.
    """
    if not (config.API_SERVICE_URL and config.API_SERVICE_TOKEN):
        return
    days_to_mailing = mailing.date_end - mailing.date_begin
    for day in range(days_to_mailing.days + 1):
        start_time = (
                datetime.combine(
                    mailing.date_begin, mailing.time_start
                ) + timedelta(days=day)
        )
        clocked = ClockedSchedule.objects.create(
            clocked_time=start_time
        )
        task = PeriodicTask.objects.create(
            name=f'{mailing.id} day {day}',
            task='mailing.tasks.distribution_mailing',
            clocked=clocked,
            start_time=start_time,
            args=f'[{mailing.id}]',
            one_off=True,
        )
        # При создании рассылки пользователь может указать время начала
        # рассылки в прошлом. Однако, для другого часового пояса это может быть
        # актуально.
        hours_difference = (datetime.now() - start_time).total_seconds() / 3600
        if start_time <= datetime.now() and hours_difference <= 26:
            # Запустим задачу вручную
            app.send_task(
                name=task.task, args=(mailing.id,)
            )
