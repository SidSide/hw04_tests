from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group, User

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовый текст',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            id=1
        )

    def setUp(self):
        self.guest_client = Client()
        self.user_not_author = User.objects.create_user(username='HasNoName')
        self.authorized_not_author = Client()
        self.authorized_not_author.force_login(self.user_not_author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_client_url_exists_at_desired_location(self):
        """Проверка доступности адресов"""
        common_pages = {
            '/': HTTPStatus.OK.value,
            f'/profile/{self.post.author}/': HTTPStatus.OK.value,
            f'/posts/{self.post.id}/': HTTPStatus.OK.value,
        }
        for address, template in common_pages.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, template)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_edit_for_author_exists_at_desired_location(self):
        """Редактирование поста автором"""
        response = self.authorized_not_author.get(
            f'/posts/{self.post.id}/edit/',
            follow=True
        )
        self.assertRedirects(response, (f'/posts/{self.post.id}/'))

    def test_unexisting_page_exists_at_desired_location(self):
        """Запрос к несуществующей странице"""
        response = self.guest_client.get('/unexist/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.authorized_client.get('/unexist/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)