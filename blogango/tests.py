from django.test  import TestCase
from models import Blog,BlogEntry,Comment
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
        #self.assertRedirects(response,reverse('blogango_install'))



    def test_single_existence(self):
        """Test that the blog is created only once """
        self.blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        self.blog.save()
        blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        #should raise Exception when another blog is created
        self.assertRaises(Exception,blog.save())
        self.blog.delete()


class TestViews(TestCase):
    """Test Views  of the blog"""

    def setUp(self):
        self.blog = Blog(title = "test",tag_line = "new blog",entries_per_page=10,recents = 5, recent_comments = 5)
        self.blog.save()
        self.c = Client()
        self.user  = User.objects.create_user(username = 'gonecrazy',email='gonecrazy@gmail.com',password = 'gonecrazy')
        self.user.is_staff = True
        self.user.save()
        

    def test_first_page(self):
        response = self.c.get( reverse("blogango_index"))
        #it should return 200 for all users
        self.assertEqual(response.status_code,200)
        
    def test_admin_page(self):
        response = self.c.get(reverse("blogango_admin_dashboard"))
        self.assertEqual(response.status_code , 200)

    def test_add_entry(self):
        """Test whether a entry can be added to the blog """
        response = self.c.login(username='gonecrazy',password='gonecrazy')
        response = self.c.post( reverse("blogango_admin_entry_new"),{'title':'test post','text':'this is the test post','publish_date_0':'2011-09-22','publish_date_1':'17:17:55','text_markup_type':"html",'created_by':1,'publish':'Save and Publish'})
        #check for successful posting of entry
        self.assertEqual(response.status_code,302)
        entries  = BlogEntry.default.all()
        self.assertEqual(1,entries.count())
        
        

    def test_entry_existence(self):
        """Test for the existence of entry"""
        entries = BlogEntry.default.all()
        print entries
        response = self.c.get('/blog/2011/09/test-post/')
        self.assertEqual(response.status_code,200)

    
    def test_edit_entry(self):
        """Test for editing a entry in the blog"""
         #edit a post .. the title is changed
        response = self.c.post( "/blog/admin/entry/edit/1/",{'title':'the new test post','text':'this is the test post','publish_date_0':'2011-09-22','publish_date_1':'17:17:55','text_markup_type':"html",'created_by':1,'publish':'Save and Publish'})     #retrieve the entry
        entry = BlogEntry.default.all()
        self.assertEqual(entry[0].title,"the new test post")

    def test_add_comment(self):
        #test if a comment can be added to entry
        entry = BlogEntry.default.all()[0]
       
        reponse = self.c.post (entry.get_absolute_url(), {'name':'gonecrazy','email':'plaban@agiliq.com',
                                                          'text':'this is a comment','button':'Comment'})
        comment = Comment.objects.filter(comment_for=entry)
        self.assertEqual(1,comment.count())
        self.assertEqual(comment.text,'this is a comment')

    def test_author_details(self):
        response = self.c.get("/blog/author/gonecrazy")
        author_posts = response.context['author_posts']
        self.assertEqual(1,author_posts.count())
    
    def tearDown(self):
        #self.blog.delete()
        #self.user.delete()
        pass

        


class TestAdminActions(TestCase):
    """check for admin action on the blog"""
    def setUp(self):
        self.c = Client()
        response = self.c.login(username='gonecrazy',password='gonecrazy')


    def test_check_adminpage(self):
        """Check that the admin page is accessible to everyone"""
        response = self.c.get(reverse('blogango_admin_dashboard'))
        self.assertEqual(response.status_code,200)

    def test_change_preferences(self):
        """check if the admin can change the preferences of blog """
        response = self.c.login(username='gonecrazy',password='gonecrazy')
        response = self.c.post(reverse('blogango_admin_edit_preferences'),{'title':'new Blog','tag_line':'my new blog',
                                                                           'entries_per_page':10,'recents':5,'recent_comments':5})
        blog = Blog.objects.all()[0]
        self.assertEqual(blog.title,'new Blog')

    def test_admin_entrymanage(self):
        """Check if all the entries are retrieved to manage"""
        response = self.c.get(reverse('blogango_admin_entry_manage'))
        entries = response.context['entries']
        self.assertEqual(1,entries.count())

    def test_admin_commentmanage(self):
        """check if all the comments are retrieved to manage"""
        response = self.c.get(reverse('blogango_admin_comments_manage'))
        comments = response.context['comments']
        self.assertEqual(1,comments.count())

    def test_admin_commentapprove(self):
        """Check if admin can properly approve a comment"""
        #first add a comment
        entry = BlogEntry.default.all()[0]
        reponse = self.c.post (entry.get_absolute_url(), {'name':'gonecrazy','email':'plaban@agiliq.com',
                                                          'text':'this is a comment','button':'Comment'})
        #check that the comment is not public
        comment = Comment.objects.filter(comment_for=entry)[-1]
        self.assertEqual(comment.is_public,False)
        #approve the comment
        
        response = self.c.get("/blog/admin/approve/comment/%s/"  % str(comment.id))
        comment = Comment.objects.filter(comment_for=entry)[-1]
        self.assertEqual(comment.is_public,True)
        
    def test_admin_commentsblock(self):
        """check if admin can block a comment properly"""
        entry = BlogEntry.default.all()[0]
        comment = Comment.objects.filter(comment_for=entry)[-1]
        self.assertEqual(comment.is_public,True )
        response = self.c.get("/blog/admin/approve/block/%s/" % str(comment.id))
        comment = Comment.objects.filter(comment_for=entry)[-1]
        self.assertEqual(comment.is_public,False)
        
        
        
        
        
        


            


        

        
        

        
        

    
          

        

        

        
        
        
    

