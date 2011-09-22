from django.utils import unittest
from models import Blog

class BlogTestCase(unittest.TestCase):
    def setUp(self):
        self.blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        self.blog.save()
    def test_single_existence(self):
        blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        self.assertRaises(Exception,blog.save())
