import pytz
from django.core.validators import RegexValidator
from django.db import models

from mailing import conts


class Mailing(models.Model):
    date_begin = models.DateField('Дата начала')
    date_end = models.DateField('Дата окончания')
    time_start = models.TimeField('Время начала')
    time_end = models.TimeField('Время окончания')
    text = models.TextField('Текст сообщения')
    operators = models.ManyToManyField(
        'MobileOperator', verbose_name='Мобильный оператор', blank=True
    )
    tags = models.ManyToManyField('Tag', verbose_name='Теги', blank=True)

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        constraints = [
            models.CheckConstraint(
                check=(
                        models.Q(date_begin__lte=models.F('date_end')) &
                        models.Q(time_start__lt=models.F('time_end'))
                ),
                name='valid_datetime_range'
            )
        ]

    def __str__(self) -> str:
        return f'{self.id} {self.date_begin} - {self.date_end}'


class Client(models.Model):
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    phone = models.CharField(
        'Номер телефона',
        max_length=11,
        validators=[RegexValidator(
            regex=r'^7\d{10}$',
            message='Номер телефона должен быть в формате 7XXXXXXXXXX',
        )]
    )
    operator = models.ForeignKey(
        'MobileOperator', on_delete=models.CASCADE,
        related_name='clients', verbose_name='Мобильный оператор'
    )
    tag = models.ForeignKey(
        'Tag', on_delete=models.CASCADE,
        related_name='clients', verbose_name='Тег',
        blank=True, null=True
    )
    timezone = models.CharField(
        'Часовой пояс', choices=TIMEZONES, max_length=255
    )

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self) -> str:
        return self.phone


class Message(models.Model):
    dc = models.DateTimeField('Дата отправки', auto_now=True)
    status = models.CharField(
        'Статус', choices=conts.STATUS_CHOICES,
        default=conts.STATUS_NOT_SENT, max_length=255
    )
    mailing = models.ForeignKey(
        'Mailing', on_delete=models.CASCADE,
        related_name='messages', verbose_name='Рассылка'
    )
    client = models.ForeignKey(
        'Client', on_delete=models.CASCADE,
        related_name='messages', verbose_name='Клиент'
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self) -> str:
        return f'{self.status} {self.client} {self.dc}'


class MobileOperator(models.Model):
    name = models.CharField('Название', max_length=255, blank=True)
    code = models.CharField(
        'Код оператора',
        max_length=3,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{3}$',
            message='Код оператора должен состоять из 3 цифр',
        )]
    )

    class Meta:
        verbose_name = 'Мобильный оператор'
        verbose_name_plural = 'Мобильные операторы'

    def __str__(self) -> str:
        return f'{self.code} - {self.name}'


class Tag(models.Model):
    name = models.CharField('Название', max_length=255)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class MailingSummary(Mailing):
    """Модель для отображения статистики в админке"""
    class Meta:
        proxy = True
        verbose_name = 'Сводка о рассылке'
        verbose_name_plural = 'Сводка о рассылках'
