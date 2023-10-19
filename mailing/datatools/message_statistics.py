from django.db.models import Count, F

from mailing import models


def get_message_statistics(mailing: models.Mailing = None) -> list[dict]:
    """
    Возвращает статистику сообщений по всем рассылкам
    либо по определенной рассылке
    """
    messages = models.Message.objects.values(
        'status', 'mailing'
    ).filter(
        mailing=mailing if mailing else F('mailing')
    ).annotate(
        count=Count('status')
    )
    data = []
    # агрегируем статистику сообщений в зависимости от статуса
    for item in messages:
        status, mailing_id, count = item.values()
        existing_item = next(
            (item for item in data if item["mailing_id"] == mailing_id), None
        )
        if existing_item:
            existing_item[status] = existing_item.get(status, 0) + count
        else:
            data.append(
                {
                    'mailing_id': mailing_id,
                    status: count,
                }
            )
    return data
