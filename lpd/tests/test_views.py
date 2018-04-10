from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from lpd.models import LearnerProfileDashboard


class UserSetup(object):
    def setUp(self):
        self.password = 'some_password'
        self.user = get_user_model().objects.create(username='student_user')
        self.user.set_password(self.password)
        self.user.save()

        self.user2 = get_user_model().objects.create(username='student_user2')
        self.user2.set_password(self.password)
        self.user2.save()

        self.lpd = LearnerProfileDashboard.objects.create(name='Test LPD')

    def login(self, username=None, password=None):
        username = username if username else self.user.username
        password = password if password else self.password
        self.assertTrue(self.client.login(username=username, password=password))


class LearnerProfileDashboardHomeViewTestCase(UserSetup, TestCase):
    def setUp(self):
        super(LearnerProfileDashboardHomeViewTestCase, self).setUp()
        self.home_url = reverse('lpd:home')

    def test_anonymous(self):
        response = self.client.get(self.home_url)
        login_url = ''.join([reverse('admin:login'), '?next=', self.home_url])
        self.assertRedirects(response, login_url)

    def test_lpd_view(self):
        self.login()
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)


class LearnerProfileDashboardCreateViewTestCase(UserSetup, TestCase):
    def setUp(self):
        super(LearnerProfileDashboardCreateViewTestCase, self).setUp()
        self.add_url = reverse('lpd:add')

    def test_anonymous(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.add_url)
        login_url = ''.join([reverse('admin:login'), '?next=', self.add_url])
        self.assertRedirects(response, login_url)

    def test_invalid(self):
        self.login()
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.add_url)
        self.assertEqual(response.status_code, 200)

    def test_valid(self):
        self.login()
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)

        post_data = {'name': 'Test LPD'}
        response = self.client.post(self.add_url, post_data)
        lpd = LearnerProfileDashboard.objects.order_by('-id')[0]
        self.assertRedirects(response, reverse('lpd:view', kwargs=dict(pk=lpd.id)))


class LearnerProfileDashboardUpdateViewTestCase(UserSetup, TestCase):
    def setUp(self):
        super(LearnerProfileDashboardUpdateViewTestCase, self).setUp()
        self.lpd = LearnerProfileDashboard.objects.create(name='Test LPD')
        self.view_url = reverse('lpd:view', kwargs=dict(pk=self.lpd.id))
        self.edit_url = reverse('lpd:edit', kwargs=dict(pk=self.lpd.id))
        self.login_url = ''.join([reverse('admin:login'), '?next=', self.edit_url])

    def test_anonymous(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.edit_url)
        self.assertRedirects(response, self.login_url)

    def test_valid(self):
        self.login()
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)

        post_data = {'name': 'Test LPD: Update'}
        response = self.client.post(self.edit_url, post_data)
        self.assertRedirects(response, self.view_url)
        response = self.client.get(self.view_url)
        self.assertEquals(response.context['object'].name, post_data['name'])
