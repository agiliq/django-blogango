from django.utils import unittest
from models import Blog,BlogEntry
from django.test.client import Client
from datetime import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class BlogTestCase(unittest.TestCase):

    def setUp(self):
        self.c = Client()

    def blog_install_redirect(self):
        #check that the blog redirects to install page when there is no blog installed    
        response = self.c.get(reverse("blogango_index"))
        self.assertEqual(response.status_code,302)

    def test_single_existence(self):
        """Test that the blog is created only once """
        #self.blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        #should raise Exception when another blog is created
        self.assertRaises(Exception,blog.save())


class TestViews(unittest.TestCase):
    """Test pages  of the blog"""
    def setUp(self):
        self.c = Client()

    def test_first_page(self):
        response = self.c.get( reverse("blogango_index"))
        #it should return 200 for all users
        self.assertEqual(response.status_code,200)
        
    def test_admin_page(self):
        response = self.c.get(reverse("blogango_admin_dashboard"))
        self.assertEqual(response.status_code , 200)

    def test_add_entry(self):
        """Test whether a entry can be added to the blog """
        user  = User.objects.create_user(username = 'gonecrazy',email='gonecrazy@gmail.com',password = 'gonecrazy')
        user.is_staff = True
        user.save()
        response = self.c.login(username='gonecrazy',password='gonecrazy')
        response = self.c.post( reverse("blogango_admin_entry_new"),{'title':'test post','text':'this is the test post','publish_date_0':'2011-09-22','publish_date_1':'17:17:55','text_markup_type':"html",'created_by':1,'publish':'Save and Publish'})
        #check for successful posting of entry
        self.assertEqual(response.status_code,302)
        blog = BlogEntry.default.all()
        print blog[0].title
        print blog[0].get_absolute_url()
        self.assertEqual(1,blog.count())
        

    def test_entry_existence(self):
        """Test for the existence of entry"""
        response = self.c.get('/blog/2011/09/test-post/')
        self.assertEqual(response.status_code,200)

    
    def test_edit_entry(self):
        """Test for editing a entry in the blog"""
        response = self.c.login(username='gonecrazy',password='gonecrazy')
        #create a post
        response = self.c.post( reverse("blogango_admin_entry_new"),{'title':'test post','text':'this is the test post','publish_date_0':'2011-09-22','publish_date_1':'17:17:55','text_markup_type':"html",'created_by':1,'publish':'Save and Publish'})
        blog = BlogEntry.default.all()[0]
        print blog.title
        #now edit the post .. the title is changed
        response = self.c.post( "/blog/admin/entry/edit/1/",{'title':'the new test post','text':'this is the test post','publish_date_0':'2011-09-22','publish_date_1':'17:17:55','text_markup_type':"html",'created_by':1,'publish':'Save and Publish'})
        #retrieve the entry
        blog = BlogEntry.default.all()[0]
        print blog.title
        self.assertEqual(blog.title,"the new test post")

        
    

        

        

        

        
        
        
    

