import random
from datetime import datetime, timedelta

import factory
from django.contrib.auth.models import User
from factory import fuzzy
from faker import Factory

from mailing import models

factory_ru = Factory.create(locale='ru_Ru')


def future_time() -> datetime.time:
    minutes = random.randint(1, 60)
    return (datetime.now() + timedelta(minutes=minutes)).time()


def past_time() -> datetime.time:
    minutes = random.randint(1, 60)
    return (datetime.now() - timedelta(minutes=minutes)).time()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: factory_ru.user_name())

    class Meta:
        model = User


class Mailing(factory.django.DjangoModelFactory):
    date_begin = factory.Sequence(
        lambda n: factory_ru.date_this_decade(before_today=True)
    )
    date_end = factory.Sequence(
        lambda n: factory_ru.future_date()
    )
    time_start = factory.Sequence(lambda n: past_time())
    time_end = factory.Sequence(lambda n: future_time())
    text = factory.Sequence(lambda n: factory_ru.text())

    class Meta:
        model = models.Mailing

    @factory.post_generation
    def operators(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.operators.add(*extracted)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.tags.add(*extracted)


class Tag(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: factory_ru.word())

    class Meta:
        model = models.Tag


class MobileOperator(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: factory_ru.word())
    code = factory.Sequence(lambda n: factory_ru.random_number(digits=3))

    class Meta:
        model = models.MobileOperator


class Client(factory.django.DjangoModelFactory):
    phone = factory.Sequence(lambda n: factory_ru.phone_number())
    operator = factory.SubFactory(MobileOperator)
    tag = factory.SubFactory(Tag)
    timezone = fuzzy.FuzzyChoice(i[0] for i in models.Client.TIMEZONES)

    class Meta:
        model = models.Client
