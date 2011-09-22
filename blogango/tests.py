from django.utils import unittest
from models import Blog
from django.test.client import Client

class BlogTestCase(unittest.TestCase):

    def setUp(self):
        self.blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        self.blog.save()
    def test_single_existence(self):
        """Test that the blog is created only once """
        blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        #should raise Exception when another blog is created
        self.assertRaises(Exception,blog.save())


class TestIndexView(unittest.TestCase):
    """Test the first page of the blog"""

    def test_first_page(self):
        c = Client()
        response = c.get("/blog/")
        self.assertEqual(response.status_code,200)
    

