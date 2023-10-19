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
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')


class TestTag(TestBase):
    def test_list_data(self) -> None:
        url = reverse('mailing:tags-list')
        response = self.client.get(url)
        tag_count = models.Tag.objects.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], tag_count)

    def test_detail(self) -> None:
        url = reverse('mailing:tags-detail', kwargs={'pk': self.tag.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.tag.name)

    def test_create(self) -> None:
        url = reverse('mailing:tags-list')
        data = {
            'name': factory_ru.word()
        }
        tags_count = models.Tag.objects.count()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Tag.objects.count(), tags_count + 1)

    def test_update(self) -> None:
        url = reverse('mailing:tags-detail', kwargs={'pk': self.tag.id})
        tag_new_name = factory_ru.word()
        data = {
            'name': tag_new_name
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], tag_new_name)
