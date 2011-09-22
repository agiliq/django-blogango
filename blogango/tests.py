from django.utils import unittest
from models import Blog,BlogEntry
from django.test.client import Client
from datetime import datetime
from django.contrib.auth.models import User
class BlogTestCase(unittest.TestCase):

    def setUp(self):
        self.blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        self.blog.save()
    def test_single_existence(self):
        """Test that the blog is created only once """
        blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        #should raise Exception when another blog is created
        self.assertRaises(Exception,blog.save())


class TestViews(unittest.TestCase):
    """Test pages  of the blog"""

    def test_first_page(self):
        c = Client()
        response = c.get("/blog/")
        #it should return 200 for all users
        self.assertEqual(response.status_code,200)
        
    def test_admin_page(self):
        c = Client()
        response = c.get("/blog/admin/")
        self.assertEqual(response.status_code , 200)

    def test_add_entry(self):
        c = Client()
        user  = User.objects.create_user('gonecrazy','gonecrazy@gmail.com','gonecrazy')
        user.is_staff = True
        user.save()
        response = c.login(username='gonecrazy',password='gonecrazy')
        response = c.post("/blog/admin/entry/new/",{'title':'my new blog post','text':'this is the test post','publish_date_0':'2011-09-22','publish_date_1':'17:17:55','text_markup_type':"html",'created_by':1})
        #check for successful posting of entry
        self.assertEqual(response.status_code,302)
        blog = BlogEntry.default.all()
        self.assertEqual(1,blog.count())
        

        

        

        
        
        
    

