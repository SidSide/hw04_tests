from django.contrib.auth import get_user_model
from django.test import TestCase

from Post.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост более 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        task_group = self.group
        expected_object_name = task_group.title
        self.assertEqual(expected_object_name, str(task_group))
        task_post = self.post
        expected_object_name = task_post.text[:15]
        self.assertEqual(expected_object_name, str(task_post))
