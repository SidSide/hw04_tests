import tempfile

from posts.models import Post, Group, User
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug1',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            id=1
        )

    def test_edit_post(self):
        post_data = {
            'text': 'Измененный тестовый текст',
            'group': self.group.id,
            'author': self.user
        }
        group_posts_count = Post.objects.filter(group=self.group).count()
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.pk, )),
            data=post_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.filter(group=self.group).count(),
                         group_posts_count)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, 'Измененный тестовый текст')
        self.assertRedirects(response, reverse('posts:post_detail',
                             args=(self.post.pk, )))

    def test_create_post(self):
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': 'auth'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
