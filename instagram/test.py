import unittest
from instagram import app


class InstagramTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def register(self, username, password):
        return self.app.post('/reg/', data={'username': username, 'password': password}, follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login/', data={'username': username, 'password': password}, follow_redirects=True)

    def logout(self):
        return self.app.get('/logout/')

    def test_register_login_logout(self):
        assert self.register('swl','123').status_code==200
        t=self.app.open('/')
        assert '--swl' in t.data
        # self.logout()
        # assert 'swl' not in self.app.open('/').data
        # self.login('swl','123')
        # assert 'swl' in self.app.open('/').data

    def test_profile(self):
        t=self.app.open('/profile/101/',follow_redirects=True)
        assert t.status_code==200
        assert 'pawword' not in t.data




    def tearDown(self):
        print 'teardown'
