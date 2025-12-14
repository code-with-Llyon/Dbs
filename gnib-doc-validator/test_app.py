import unittest
from datetime import datetime, timedelta
from app import allowed_file, passport_is_valid


class TestFileValidation(unittest.TestCase):

    def test_allowed_extensions(self):
        self.assertTrue(allowed_file("passport.pdf"))
        self.assertTrue(allowed_file("photo.jpg"))
        self.assertTrue(allowed_file("scan.PNG"))

    def test_disallowed_extensions(self):
        self.assertFalse(allowed_file("notes.txt"))
        self.assertFalse(allowed_file("script.exe"))
        self.assertFalse(allowed_file("image"))


class TestPassportExpiry(unittest.TestCase):

    def test_valid_passport(self):
        future_date = (datetime.today() + timedelta(days=365)
                       ).strftime("%Y-%m-%d")
        self.assertTrue(passport_is_valid(future_date))

    def test_expired_passport(self):
        past_date = (datetime.today() - timedelta(days=365)
                     ).s
