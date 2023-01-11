import tempfile

from posts.models import Post, Group, User
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоватьсяgs
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
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
            'text': 'Тестовый текст',
            'group': self.group.id,
            'author': self.user
        }
        group_posts_count = Post.objects.filter(group=self.group.id).count()
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.pk, )),
            data=post_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.filter(group=self.group.id).count(),
                         group_posts_count)

        self.assertTrue(Post.objects.filter(
            id=self.post.pk,
            text='Тестовый текст',
            group=self.group.id,
            author=self.user,
        ).exists())
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
