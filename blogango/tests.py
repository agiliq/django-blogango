import re
import logging
import blogango.utils
import pprint
import sys

from django.test  import TestCase
from models import Blog,BlogEntry,Comment
from django.test.client import Client
from datetime import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

logger = logging.getLogger(__name__)

class BlogInstallTestCase(TestCase):

    def setUp(self):
        self.c = Client()
        self.user  = User.objects.create_user(username = 'admin',email='admin@email.com',password = 'admin')
        self.user.is_staff = True
        self.user.save()
        self.c.login(username='admin',password='admin')


    def test_bloginstall_redirect(self):
        #check that the blog redirects to install page when there is no blog installed
        response = self.c.get(reverse("blogango_index"),follow=True)
        self.assertRedirects(response,reverse('blogango_install'))
        self.assertTrue(re.search(r'<input name="install" type="submit" value="Install Blog" class="button"/>',response.content))


    def test_single_existence(self):
        """Test that the blog is created only once """
        self.blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        self.blog.save()
        blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        #should raise Exception when another blog is created
        self.assertRaises(Exception,blog.save())

class BlogWithUser(TestCase):

    def setUp(self):
        self.blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        self.blog.save()
        self.c = Client()
        self.user  = User.objects.create_user(username = 'admin',email='admin@gmail.com',password = 'admin')
        self.user.is_staff = True
        self.user.save()
        response = self.c.login(username='admin',password='admin')

class BlogIndexPageTest(BlogWithUser):

    def test_first_page(self):
        response = self.c.get( reverse("blogango_index"))
        #it should return 200 for all users
        self.assertEqual(response.status_code,200)

class BlogAdminPageTest(BlogWithUser):

    def test_admin_page(self):
        response = self.c.get(reverse("blogango_admin_dashboard"))
        self.assertEqual(response.status_code , 200)


class BlogWithAnEntry(BlogWithUser):
    def setUp(self):
        BlogWithUser.setUp(self)
        self.c.post(reverse("blogango_admin_entry_new"),
                {
                    'title':'test post',
                    'text':'this is the test post',
                    'publish_date_0':'2011-09-22','publish_date_1':'17:17:55',
                    'created_on_0':'2011-09-22','created_on_1':'17:17:55',
                    'text_markup_type':"html",
                    'created_by':1,
                    'publish':'Save and Publish'
                })


class BlogEntryTest(BlogWithAnEntry):

    def test_add_entry(self):
        entries  = BlogEntry.default.all()
        self.assertEqual(1,entries.count())

    def test_entry_existence(self):
        """Test for the existence of entry"""
        entries = BlogEntry.default.all()
        response = self.c.get('/blog/2011/09/test-post/')
        self.assertEqual(response.status_code,200)

    def test_edit_entry(self):
        """Test for editing a entry in the blog"""
         #edit a post .. the title is changed
        self.c.post( "/blog/admin/entry/edit/1/",
                {
                    'title':'test new post',
                    'text':'this is edited post',
                    'publish_date_0':'2011-09-22','publish_date_1':'17:17:55',
                    'created_on_0':'2011-09-22','created_on_1':'17:17:55',
                    'text_markup_type':"html",
                    'created_by':1,
                    'publish':'Save and Publish'
                })

        entry = BlogEntry.default.all()
        self.assertEqual(entry[0].title,"test new post")

    def test_author_details(self):
        response = self.c.get("/blog/author/admin/")
        author_posts = response.context['author_posts']
        self.assertEqual(1,author_posts.count())

class BlogCommentTest(BlogWithAnEntry):

    def test_add_comment(self):
        #test if a comment can be added to entry
        entry = BlogEntry.default.all()[0]

        reponse = self.c.post (entry.get_absolute_url(), {'name':'admingonecrazy','email':'plaban@agiliq.com',
                                                          'text':'this is a comment','button':'Comment'})
        comments = Comment.objects.filter(comment_for=entry)
        self.assertEqual(1,comments.count())
        self.assertEqual(comments[0].text,'this is a comment')


class TestAdminActions(BlogWithAnEntry):

    def test_check_adminpage(self):
        """Check that the admin page is accessible to everyone"""
        response = self.c.get(reverse('blogango_admin_dashboard'))
        self.assertEqual(response.status_code,200)

    def test_change_preferences(self):
        """check if the admin can change the preferences of blog """
        response = self.c.post(reverse('blogango_admin_edit_preferences'),{'title':'new Blog','tag_line':'my new blog',
                                                                           'entries_per_page':10,'recents':5,'recent_comments':5})
        blog = Blog.objects.all()[0]
        self.assertEqual(blog.title,'new Blog')

    def test_admin_entrymanage(self):
        """Check if all the entries are retrieved to manage"""
        response = self.c.get(reverse('blogango_admin_entry_manage'))
        entries = response.context['entries']
        self.assertEqual(1,entries.count())

    def test_admin_comment_approve_block(self):
        """Check if admin can properly approve a comment"""
        #first add a comment
        entry = BlogEntry.default.all()[0]
        reponse = self.c.post (entry.get_absolute_url(), {'name':'gonecrazy','email':'plaban@agiliq.com',
                                                          'text':'this is a comment','button':'Comment'})

        comment = Comment.objects.filter(comment_for=entry).reverse()[0]
        logger.debug("The comment's id is %s" % str(comment.id))
        old_flag = comment.is_public
        self.c.get("/blog/admin/comment/block/%s/" % str(comment.id))
        self.c.get("/blog/admin/comment/approve/%s/"  % str(comment.id))
        comment = Comment.objects.filter(comment_for=entry).reverse()[0]
        new_flag = comment.is_public
        self.assertTrue(old_flag == new_flag)

    def test_admin_commentmanage(self):
        """check if all the comments are retrieved to manage"""
        entry = BlogEntry.default.all()[0]
        reponse = self.c.post (entry.get_absolute_url(), {'name':'gonecrazy','email':'plaban@agiliq.com',
                                                          'text':'this is a comment','button':'Comment'})
        response = self.c.get(reverse('blogango_admin_comments_manage'))
        comments = response.context['comments']
        self.assertEqual(1,comments.count())

