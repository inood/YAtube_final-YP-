from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserProfilTest(TestCase):

	def setUp(self):
		self.client = Client()
		self.username = 'Onotoly'
		self.email = 'vassa@rm.an'
		self.password = 'P@ssw0rd01!'

	def test_noreg_user_profile(self):
		response_nonreg_user = self.client.get(
			reverse('profile'), {'username': 'kakoytoIvan'}
		)
		self.assertEqual(response_nonreg_user.status_code, 404)

	def test_signup_user_profile(self):
		response = self.client.get(
			reverse('profile', kwargs={'username': self.username})
		)
		self.assertEqual(response.status_code, 404)

		self.client.post(reverse('signup'), data={
			'username': self.username,
			'email': self.email,
			'password1': self.password,
			'password2': self.password
		})
		user = User.objects.last()
		self.assertEqual(user.username, self.username)

		response_reg_user = self.client.get(
			reverse('profile', kwargs={'username': user.username})
		)
		self.assertEqual(response_reg_user.status_code, 200)
