from django.urls import reverse
from faker import Factory
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from mailing import factories, models

factory_ru = Factory.create(locale='ru_Ru')


class TestBase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = factories.UserFactory()
        self.tag = factories.Tag()
        self.operator = factories.MobileOperator()
        self.mailing = factories.Mailing(
            tags=(self.tag,), operators=(self.operator,)
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')


class TestMailing(TestBase):
    def test_list_data(self) -> None:
        url = reverse('mailing:mailings-list')
        response = self.client.get(url)
        mailing_count = models.Mailing.objects.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], mailing_count)

    def test_detail(self) -> None:
        url = reverse(
            'mailing:mailings-detail', kwargs={'pk': self.mailing.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['date_begin'], str(self.mailing.date_begin)
        )

    def test_create(self) -> None:
        url = reverse('mailing:mailings-list')
        tag = factories.Tag()
        operator = factories.MobileOperator()
        data = {
            'date_begin': factory_ru.date_this_decade(before_today=True),
            'date_end': factory_ru.future_date(),
            'time_start': factories.past_time(),
            'time_end': factories.future_time(),
            'text': factory_ru.text(),
            'tags': [tag.id],
            'operator': [operator.id],
        }
        operator_count = models.Mailing.objects.count()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Mailing.objects.count(), operator_count + 1)

    def test_update(self) -> None:
        url = reverse(
            'mailing:mailings-detail', kwargs={'pk': self.mailing.id}
        )
        mailing_new_text = factory_ru.text()
        data = {
            'text': mailing_new_text,
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], mailing_new_text)
