from django.urls import reverse
from faker import Factory
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from mailing import factories, models

factory_ru = Factory.create(locale='ru_Ru')


class TestBase(APITestCase):
    def setUp(self) -> None:
        self.api_client = APIClient()
        self.user = factories.UserFactory()
        self.client = factories.Client(phone='79999999999')
        self.token = Token.objects.create(user=self.user)
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')


class TestClient(TestBase):
    def test_list_data(self) -> None:
        url = reverse('mailing:clients-list')
        response = self.api_client.get(url)
        client_count = models.Client.objects.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], client_count)

    def test_detail(self) -> None:
        url = reverse(
            'mailing:clients-detail', kwargs={'pk': self.client.id}
        )
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['operator'], self.client.operator.id)

    def test_create(self) -> None:
        url = reverse('mailing:clients-list')
        tag = factories.Tag()
        operator = factories.MobileOperator()
        timezone = 'Asia/Yekaterinburg'
        data = {
            'phone': '78888888888',
            'timezone': timezone,
            'tag': tag.id,
            'operator': operator.id,
        }
        client_count = models.Client.objects.count()
        response = self.api_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            models.MobileOperator.objects.count(), client_count + 1
        )

    def test_update(self) -> None:
        url = reverse('mailing:clients-detail', kwargs={'pk': self.client.id})
        operator = factories.MobileOperator()
        data = {
            'operator': operator.id
        }
        response = self.api_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['operator'], operator.id)
