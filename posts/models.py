from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Название', max_length=200)
    slug = models.SlugField(verbose_name='Slug', unique=True)
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self):
        return f'{self.pk}: {self.title}'

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField(verbose_name='Содержание')
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='author_posts')
    group = models.ForeignKey(Group, verbose_name='Группа',
                              on_delete=models.SET_NULL,
                              related_name='group_posts',
                              blank=True, null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return f'{self.author}: {self.text[:12]}'

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

class Comment(models.Model):
    post = models.ForeignKey(Post, verbose_name='Статья',
                             on_delete=models.CASCADE,
                             related_name='comment_post',)
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='comment_author')
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(verbose_name='Дата комментария',
                                   auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
