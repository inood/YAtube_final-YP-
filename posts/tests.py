import time

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Follow, Group, Post, Comment

User = get_user_model()


class NewPostsTest(TestCase):

	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(
			username='testuser',
			email='testuser@testserver.com',
			password='qwerty'
		)

	def test_create_new_post_auth_user(self):
		new_text = 'Текст нового поста'
		self.client.force_login(self.user)
		self.client.post(
			reverse('new_post'), {'text': new_text})
		self.assertEqual(Post.objects.count(), 1)

	def test_get_new_post_anon_user(self):
		self.client.logout()
		new_text = 'Текст нового поста'
		response = self.client.post(
			reverse('new_post'), {'text': new_text})
		self.assertRedirects(response, '/auth/login/?next=/new/')
		self.assertEquals(Post.objects.count(), 0)


class PostViewTest(TestCase):

	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(
			username='testuser',
			email='testuser@testserver.com',
			password='qwerty'
		)
		self.post = Post.objects.create(
			text='new post text',
			author=self.user
		)
		self.urls_check = [
			reverse('index'),
			reverse('profile', kwargs={'username': self.user}),
			reverse(
				'post_edit',
				kwargs={'username': self.user, 'post_id': self.post.id}
			)
		]
		self.client.force_login(self.user)

	def test_check_new_post_all_view(self):
		for url in self.urls_check:
			with self.subTest(url=url):
				response = self.client.get(url)
				self.assertContains(response, self.post.text)


class PostTestEdit(TestCase):

	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(
			username='testuser',
			email='testuser@testserver.com',
			password='qwerty'
		)
		self.post = Post.objects.create(
			text='новая запись поста',
			author=self.user
		)
		self.modification_text = 'Какой-то текст на который мы изменим пост'
		self.url_edit_post = reverse(
			'post_edit',
			kwargs={'username': self.user, 'post_id': self.post.id}
		)
		self.url_post = reverse(
			'post_retrieve',
			kwargs={'username': self.user, 'post_id': self.post.id}
		)
		self.urls_check = [
			reverse('index'),
			reverse('profile', kwargs={'username': self.user}),
			reverse(
				'post_edit',
				kwargs={'username': self.user, 'post_id': self.post.id}
			)
		]
		self.client.force_login(self.user)

	def test_available_post_edit_view(self):
		response = self.client.get(self.url_edit_post)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.post.text)

	def test_modification_post(self):
		response = self.client.post(
			self.url_edit_post, {'text': self.modification_text}
		)
		self.assertEqual(Post.objects.count(), 1)
		self.assertEqual(Post.objects.last().text, self.modification_text)
		self.assertRedirects(response, self.url_post)

	def test_available_change_post_all_view(self):
		self.post.text = self.modification_text
		self.client.force_login(self.user)
		self.post.save()

		for url in self.urls_check:
			with self.subTest(url=url):
				response = self.client.get(url)
				self.assertContains(response, self.modification_text)


class ErrorPageTest(TestCase):

	def test_404_page(self):
		response = self.client.get('my/pandom/page')
		self.assertEqual(response.status_code, 404)


class ImageTest(TestCase):

	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(
			username='testuser',
			email='testuser@testserver.com',
			password='qwerty'
		)
		self.group = Group.objects.create(
			title='new_group', slug='ng',
			description='desc')

		self.post = Post.objects.create(
			text='Новый пост без картинки',
			author=self.user,
			group=self.group)

		self.urls_check = [
			reverse('index'),
			reverse('profile', kwargs={'username': self.user}),
			reverse('group', kwargs={'slug': self.group.slug}),
			reverse('post_retrieve', kwargs={
				'username': self.user,
				'post_id': self.post.id})
		]

	def test_image_tag_on_page(self):
		self.client.force_login(self.user)
		with open('media/test.jpeg', 'rb') as img:
			response = self.client.post(
				reverse('post_edit', kwargs={
					'username': self.user,
					'post_id': self.post.id}),
				{'text': 'post edit', 'image': img, 'group': self.group.id},
				follow=True
			)
		self.assertRedirects(response, reverse(
			'post_retrieve', kwargs={
				'username': self.user,
				'post_id': self.post.id}))

		for url in self.urls_check:
			with self.subTest(url=url):
				response = self.client.get(url)
				self.assertContains(response, "card-img", status_code=200)

	def test_alter_file_format(self):
		self.client.force_login(self.user)
		with open('media/test.test', 'rb') as img:
			response = self.client.post(
				reverse('post_edit', kwargs={
					'username': self.user,
					'post_id': self.post.id}),
				{'text': 'новый пост с картинкой', 'image': img}, follow=True
			)
			self.assertTrue(response.context['form'].has_error('image'))


class CacheTest(TestCase):

	def setUp(self):
		self.text = 'New post in test.'
		self.client = Client()
		self.user = User.objects.create_user(
			username='testuser',
			email='testuser@testserver.com',
			password='qwerty'
		)
		self.client.force_login(self.user)

	def test_index_page_cahe(self):
		self.client.get(reverse('index'))
		self.client.post(reverse('new_post'), {
			'text': self.text})
		response = self.client.get(reverse('index'))
		self.assertNotContains(
			response,
			self.text)
		time.sleep(21)
		response = self.client.get(reverse('index'))
		self.assertContains(
			response,
			self.text)


class SubscribeTest(TestCase):

	def setUp(self):
		self.text = 'New post in test.'
		self.client = Client()
		self.main_user = User.objects.create_user(
			username='mainuser',
			email='mainuser@mainuser.com',
			password='qwerty'
		)
		self.followed_user = User.objects.create_user(
			username='followeduser',
			email='followeduser@followeduser.com',
			password='qwerty'
		)
		self.unfollowed_user = User.objects.create_user(
			username='unfolloweduser',
			email='unfolloweduser@followeduser.com',
			password='qwerty'
		)
		self.post_follow = Post.objects.create(
			text='Новый пост пользователя на которого я подписан',
			author=self.followed_user,
		)
		self.post_unfollow = Post.objects.create(
			text='Новый пост пользователя на которого я не подписан',
			author=self.unfollowed_user,
		)
		self.client.force_login(self.main_user)

	def test_auth_subscribe(self):
		follower = Follow.objects.last()
		self.assertIsNone(follower)
		self.client.get(reverse(
			'profile_follow', kwargs={'username': self.followed_user})
		)
		follower = Follow.objects.last()
		self.assertIsNotNone(follower)
		self.client.get(reverse(
			'profile_unfollow', kwargs={'username': self.followed_user})
		)
		follower = Follow.objects.last()
		self.assertIsNone(follower)

	def test_newpost_in_subscribe_list(self):
		self.client.get(reverse(
			'profile_follow', kwargs={'username': self.followed_user})
		)
		response = self.client.get(reverse('follow_index'))
		self.assertContains(response, self.post_follow.text)
		self.assertNotContains(response, self.post_unfollow.text)


class CommentTest(TestCase):

	def setUp(self):
		self.text = 'First Comment'
		self.client = Client()
		self.user = User.objects.create_user(
			username='testuser',
			email='testuser@testuser.com',
			password='qwerty'
		)
		self.client.force_login(self.user)
		self.post = Post.objects.create(
			text='Новый пост для комментариев',
			author=self.user,
		)

	def test_auth_comment(self):
		comment = Comment.objects.last()
		self.assertIsNone(comment)
		self.text = 'Первый коммент'
		self.client.post(reverse(
			'add_comment',
			kwargs={
				'username': self.user,
				'post_id': self.post.id
			}), {'text': self.text}
		)
		comment = Comment.objects.last()
		self.assertIsNotNone(comment)

	def test_non_auth_comment(self):
		self.client.logout()
		response = self.client.get(reverse(
			'add_comment',
			kwargs={
				'username': self.user,
				'post_id': self.post.id
			}
		))
		self.assertRedirects(
			response,
			f'/auth/login/?next=/{self.user}/{self.post.id}/comment/'
		)
