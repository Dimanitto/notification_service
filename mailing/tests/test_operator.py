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
        self.operator = factories.MobileOperator()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')


class TestMobileOperator(TestBase):
    def test_list_data(self) -> None:
        url = reverse('mailing:mobile_operators-list')
        response = self.client.get(url)
        operator_count = models.MobileOperator.objects.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], operator_count)

    def test_detail(self) -> None:
        url = reverse(
            'mailing:mobile_operators-detail', kwargs={'pk': self.operator.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], str(self.operator.code))

    def test_create(self) -> None:
        url = reverse('mailing:mobile_operators-list')
        data = {
            'name': factory_ru.word(),
            'code': factory_ru.random_number(digits=3),
        }
        operator_count = models.MobileOperator.objects.count()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            models.MobileOperator.objects.count(), operator_count + 1
        )

    def test_update(self) -> None:
        url = reverse(
            'mailing:mobile_operators-detail', kwargs={'pk': self.operator.id}
        )
        operator_new_code = factory_ru.random_number(digits=3)
        data = {
            'code': operator_new_code
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], str(operator_new_code))
