import unittest
from flask import current_app
from app import create_app, db

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):   # Testing ensures that the application instance exists
        self.assertFalse(current_app is None)   #current_app

    def test_app_is_testing(self): # Testing ensures that the application is running under the testing configuration
        self.assertTrue(current_app.config['TESTING'])   #current_app
