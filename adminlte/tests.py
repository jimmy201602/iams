# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User,AnonymousUser
from django.test import Client

class AdminlteTests(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret',
        }
        User.objects.create_user(**self.credentials)
        
    def test_login_page(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)
        
    def test_index_permission(self):
        resp = self.client.get(reverse('adminlte-index'))
        self.assertEqual(resp.status_code, 302)
        #login
        c = Client()
        response = c.post(reverse('login'), self.credentials)
        self.assertEqual(c.get(reverse('adminlte-index')).status_code,200)
        
    def test_user_login(self):
        resp = self.client.post(reverse('login'),self.credentials,follow=True) 
        self.assertTrue(resp.wsgi_request.user.is_authenticated())        