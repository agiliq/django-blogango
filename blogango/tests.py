from django.test  import TestCase
from models import Blog,BlogEntry
from django.test.client import Client
from datetime import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class BlogTestCase(TestCase):

    def setUp(self):
        self.c = Client()

    def test_bloginstall_redirect(self):
        #check that the blog redirects to install page when there is no blog installed    
        response = self.c.get(reverse("blogango_index"))
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,reverse('blogango_install'))
        response = self.c.get(reverse("blogango_install"))


    def test_single_existence(self):
        """Test that the blog is created only once """
        self.blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        self.blog.save()
        blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        #should raise Exception when another blog is created
        self.assertRaises(Exception,blog.save())


class TestViews(TestCase):
    """Test pages  of the blog"""

    def setUp(self):
        self.blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        self.blog.save()
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
        entries  = BlogEntry.default.all()
        self.assertEqual(1,entries.count())
        

    def test_entry_existence(self):
        """Test for the existence of entry"""
        response = self.c.get('/blog/2011/09/test-post/')
        self.assertEqual(response.status_code,200)

    
    def test_edit_entry(self):
        """Test for editing a entry in the blog"""
        response = self.c.login(username='gonecrazy',password='gonecrazy')
         #edit a post .. the title is changed
        response = self.c.post( "/blog/admin/entry/edit/1/",{'title':'the new test post','text':'this is the test post','publish_date_0':'2011-09-22','publish_date_1':'17:17:55','text_markup_type':"html",'created_by':1,'publish':'Save and Publish'})       #retrieve the entry
        entry = BlogEntry.default.all()[0]
        print entry.title
        self.assertEqual(blog.title,"the new test post")

        
          

        

        

        
        
        
    

