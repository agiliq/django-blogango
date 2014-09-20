from django.test  import TestCase
from django.test.client import Client
from datetime import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management import call_command
from django.core import mail


from taggit.models import Tag
from .models import Blog, BlogEntry, Comment


class BlogTestCase(TestCase):

    def setUp(self):
        self.c = Client()

    def test_bloginstall_redirect(self):
        "check that the blog redirects to install page when there is no blog installed"
        response = self.c.get(reverse("blogango_index"))
        self.assertEqual(response.status_code, 302)

    def test_blogindex_access(self):
        Blog.objects.create(title='test', tag_line="blog",
                entries_per_page=10, recents=5, recent_comments=5)
        response = self.c.get(reverse("blogango_index"))
        self.assertEqual(response.status_code, 200)
        User.objects.create_user(username='foo', password='bar')
        self.c.login(username='foo', password='bar')
        response = self.c.get(reverse('blogango_install'))
        self.assertEqual(response.status_code, 302)

    def test_bloginstall(self):
        User.objects.create_user(username='foo', password='bar')
        response = self.c.get(reverse('blogango_install'))
        self.assertEqual(response.status_code, 200)
        self.c.login(username='foo', password='bar')
        response = self.c.get(reverse('blogango_install'))
        self.assertEqual(response.status_code, 200)

    def test_single_existence(self):
        """Test that the blog is created only once """
        self.blog = Blog(title="test", tag_line="new blog", entries_per_page=10,
                        recents=5, recent_comments=5)
        self.blog.save()
        blog = Blog(title="test", tag_line="new blog", entries_per_page=10,
                    recents=5, recent_comments=5)
        #should raise Exception when another blog is created
        self.assertRaises(Exception, blog.save)
        blog = Blog.objects.get()
        blog.title = 'edited'
        blog.save()
        self.assertEqual(Blog.objects.count(), 1)
        self.assertEqual(Blog.objects.get().title, 'edited')


class TestBlogEntry(TestCase):
    def setUp(self):
        self.blog = Blog(title="test", tag_line="new blog", entries_per_page=10,
                    recents=5, recent_comments=5)
        self.blog.save()
        self.c = Client()
        self.user = User.objects.create_user(username='gonecrazy', email='gonecrazy@gmail.com', password='gonecrazy')
        self.user.is_staff = True
        self.user.save()

    def test_blogentry_managers(self):
        """Test custom manager works as expected"""
        e1 = BlogEntry.objects.create(title="test", text='foo', created_by=self.user,
                    publish_date=datetime.today(), text_markup_type='plain',
                    is_published=False)
        e2 = BlogEntry.objects.create(title="test", text='foo', created_by=self.user,
                    publish_date=datetime.today(), text_markup_type='plain',
                    is_published=True)
        self.assertEqual(BlogEntry.default.count(), 2)
        self.assertEqual(BlogEntry.objects.count(), 1)


class TestViews(TestCase):
    """Test Views  of the blog"""

    def setUp(self):
        self.blog = Blog(title="test", tag_line="new blog", entries_per_page=10,
                    recents=5, recent_comments=5)
        self.blog.save()
        self.c = Client()
        self.user = User.objects.create_user(username='gonecrazy', email='gonecrazy@gmail.com', password='gonecrazy')
        self.user.is_staff = True
        self.user.save()

    def test_first_page(self):
        response = self.c.get(reverse("blogango_index"))
        #it should return 200 for all users
        self.assertEqual(response.status_code, 200)

    def test_entries_pagination(self):
        num_entries = 15
        for each in range(num_entries):
            BlogEntry.objects.create(title="test", text='foo', created_by=self.user,
                    publish_date=datetime.today(), text_markup_type='plain')
        self.assertEqual(BlogEntry.objects.count(), 15)
        response = self.c.get(reverse('blogango_page', args=[1]))
        self.assertEqual(response.status_code, 200)
        response = self.c.get(reverse('blogango_page', args=[2]))
        self.assertEqual(response.status_code, 200)
        response = self.c.get(reverse('blogango_page', args=[3]))
        self.assertEqual(response.status_code, 404)

    def test_entries_slug(self):
        e1 = BlogEntry.objects.create(title="test", text='foo', created_by=self.user,
                    publish_date=datetime.today(), text_markup_type='plain')
        e2 = BlogEntry.objects.create(title="test", text='foo', created_by=self.user,
                    publish_date=datetime.today(), text_markup_type='plain')
        self.assertEqual(e1.slug, "test")
        self.assertEqual(e2.slug, "test-2")
        e1 = BlogEntry.objects.get(pk=e1.pk)
        e2 = BlogEntry.objects.get(pk=e2.pk)
        e1.save()
        self.assertEqual(e1.slug, "test")
        self.assertEqual(e2.slug, "test-2")
        e3 = BlogEntry.objects.create(title="test", text='foo', created_by=self.user,
                    publish_date=datetime.today(), text_markup_type='plain')
        self.assertEqual(e3.slug, "test-3")

    def test_tags_url(self):
        e1 = BlogEntry.objects.create(title="test", text='foo', created_by=self.user,
                    publish_date=datetime.today(), text_markup_type='plain')
        e2 = BlogEntry.objects.create(title="test", text='foo', created_by=self.user,
                    publish_date=datetime.today(), text_markup_type='plain')
        e1.tags.add("test1", "test2")
        e2.tags.add("test1")
        response = self.c.get(reverse('blogango_tag_details', args=['test1']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['entries']), 2)
        response = self.c.get(reverse('blogango_tag_details', args=['test2']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['entries']), 1)

    def test_entry_existence(self):
        """Test for the existence of entry"""
        BlogEntry.objects.create(**{'title': 'test post',
            'text': 'this is the test post',
            'publish_date': datetime.strptime("2011-09-22", "%Y-%m-%d"),
            'text_markup_type': "html",
            'created_by': self.user})
        response = self.c.get(reverse('blogango_details', args=['2011', '09', 'test-post']))
        self.assertEqual(response.status_code, 200)

    def test_add_comment(self):
        #test if a comment can be added to entry
        create_test_blog_entry(self.user)
        entry = BlogEntry.default.all()[0]
        reponse = self.c.post(entry.get_absolute_url(), {'name': 'gonecrazy', 'email': 'plaban@agiliq.com',
                                                          'text': 'this is a comment', 'button': 'Comment'})
        comment = Comment.objects.get(comment_for=entry)
        comments = Comment.objects.filter(comment_for=entry)
        self.assertEqual(comments.count(), 1)
        self.assertEqual(comment.text, 'this is a comment')

    def test_author_details(self):
        create_test_blog_entry(self.user)
        response = self.c.get("/blog/author/%s/" % self.user.username)
        entries = response.context['entries']
        self.assertEqual(1, entries.count())

    def test_author_entries_pagination(self):
        num_entries = 15
        for each in range(num_entries):
            BlogEntry.objects.create(title="test", text='foo', created_by=self.user,
                    publish_date=datetime.today(), text_markup_type='plain')
        self.assertEqual(BlogEntry.objects.count(), 15)
        response = self.c.get(reverse('blogango_author_page', args=[self.user.username])+'?page=1')
        self.assertEqual(response.status_code, 200)
        response = self.c.get(reverse('blogango_author_page', args=[self.user.username])+'?page=2')
        self.assertEqual(response.status_code, 200)
        response = self.c.get(reverse('blogango_author_page', args=[self.user.username])+'?page=3')
        self.assertEqual(response.status_code, 404)

    def test_tagged_entries_pagination(self):
        num_entries = 15
        for each in range(num_entries):
            entry = BlogEntry.objects.create(title="test", text='foo', created_by=self.user,
                        publish_date=datetime.today(), text_markup_type='plain')
            entry.tags.add("taggit")
        tag = Tag.objects.get(name='taggit')
        self.assertEqual(BlogEntry.objects.count(), 15)
        response = self.c.get(reverse('blogango_tag_details_page', args=[tag.slug, 1]))
        self.assertEqual(response.status_code, 200)
        response = self.c.get(reverse('blogango_tag_details_page', args=[tag.slug, 2]))
        self.assertEqual(response.status_code, 200)
        response = self.c.get(reverse('blogango_tag_details_page', args=[tag.slug, 3]))
        self.assertEqual(response.status_code, 404)


class TestAdminActions(TestCase):
    """check for admin action on the blog"""
    def setUp(self):
        self.c = Client()
        self.blog = Blog(title="test", tag_line="new blog", entries_per_page=10, recents=5, recent_comments=5)
        self.blog.save()
        self.user = User.objects.create_user(username='gonecrazy', email='gonecrazy@gmail.com', password='gonecrazy')
        self.user.is_staff = True
        self.user.save()
        response = self.c.login(username='gonecrazy', password='gonecrazy')
        entry = create_test_blog_entry(self.user)
        create_test_comment(entry)

    def test_check_adminpage(self):
        """Check that the admin page is accessible to only staff members"""
        response = self.c.get(reverse('blogango_admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("admin/login.html")
        self.c.login(username='gonecrazy', password='gonecrazy')
        response = self.c.get(reverse('blogango_admin_dashboard'))
        self.assertTemplateNotUsed("admin/login.html")

    def test_add_entry(self):
        """Test whether a entry can be added to the blog """
        self.assertEqual(BlogEntry.objects.count(), 1)
        response = self.c.login(username='gonecrazy', password='gonecrazy')
        #Test posting invalid form
        data = {'text_markup_type': 'html', 'created_by':self.user.pk}
        response = self.c.post(reverse("blogango_admin_entry_new"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "text", "This field is required.")
        self.assertFormError(response, "form", "tags", "This field is required.")
        #post a valid form but don't publish it
        data['text'] = 'test text'
        data['publish_date_0'] = '2011-09-22'
        data['publish_date_1'] = '17:17:55'
        data['tags'] = 'testing, testing2'
        data['save'] = 'Save'
        response = self.c.post(reverse("blogango_admin_entry_new"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BlogEntry.default.count(), 2)
        self.assertEqual(BlogEntry.objects.count(), 1)
        #post valid data and publish it
        del data['save']
        data['publish'] = 'Save and Publish'
        response = self.c.post(reverse("blogango_admin_entry_new"), data)
        self.assertEqual(BlogEntry.objects.count(), 2)
        entry = BlogEntry.objects.latest('pk')
        #check proper tags have been set
        self.assertEqual([each.name for each in entry.tags.all()], ["testing", "testing2"])

    def test_edit_entry(self):
        """Test for editing a entry in the blog"""
        self.c.login(username='gonecrazy', password='gonecrazy')
        #edit a post .. the title is changed
        post = BlogEntry.objects.create(**{'title': 'test post',
                    'text': 'this is the test post',
                    'publish_date': datetime.strptime("2011-09-22", "%Y-%m-%d"),
                    'text_markup_type': "html",
                    'created_by': self.user})
        post.tags.add("test", "another test")
        self.assertEqual([each.name for each in post.tags.all()], ["test", "another test"])
        response = self.c.post("/blog/admin/entry/edit/%s/" % post.pk,
                {'title': 'the new test post', 'text': 'this is the test post',
                'publish_date_0': '2011-09-22', 'publish_date_1': '17:17:55',
                'text_markup_type': "html", 'created_by': self.user.pk, 'publish': 'Save and Publish',
                'tags': 'testing'})
        self.assertEqual(response.status_code, 302)
        entry = BlogEntry.objects.get(pk=post.pk)
        self.assertEqual(entry.title, "the new test post")
        self.assertEqual([each.name for each in entry.tags.all()], ["testing"])

    def test_change_preferences(self):
        """check if the admin can change the preferences of blog """
        self.c.post(reverse('blogango_admin_edit_preferences'), {'title': 'new Blog', 'tag_line': 'my new blog',
                                                                           'entries_per_page': 10, 'recents': 5, 'recent_comments': 5})
        blog = Blog.objects.get_blog()
        self.assertEqual(blog.title, 'new Blog')

    def test_admin_entrymanage(self):
        """Check if all the entries are retrieved to manage"""
        response = self.c.get(reverse('blogango_admin_entry_manage'))
        entries = response.context['entries']
        self.assertEqual(1, entries.count())

    def test_admin_author_entry_manage(self):
        """Check if we can manage entries by a specific author"""
        user = User.objects.create_superuser("test", "test@agiliq.com", "test")
        create_test_blog_entry(user)
        response = self.c.get(reverse('blogango_admin_author_entry_manage', args=["test"]))
        entries = response.context['entries']
        self.assertEqual(entries.count(), 1)
        self.assertEqual(BlogEntry.default.count(), 2)

    def test_admin_commentmanage(self):
        """check if all the comments are retrieved to manage"""
        response = self.c.get(reverse('blogango_admin_comments_manage'))
        comments = response.context['comments']
        self.assertEqual(1, comments.count())

    def test_manage_entry_comments(self):
        """Check if there is a page to see comments for a particular entry"""
        user = User.objects.create_superuser("test", "test@agiliq.com", "test")
        entry = create_test_blog_entry(user)
        create_test_comment(entry)
        response = self.c.get(reverse('blogango_admin_entry_comments_manage', args=[entry.pk]))
        comments = response.context['comments']
        self.assertEqual(1, comments.count())


class TestStaticFiles(TestCase):
    """Check if app contains required static files"""
    def test_images(self):
        abs_path = finders.find('blogango/images/agiliq_blog_logo.png')
        self.assertIsNotNone(abs_path)
        abs_path = finders.find('blogango/images/person_default.jpg')
        self.assertIsNotNone(abs_path)
        abs_path = finders.find('logango/images/person_default.jpg')
        self.assertIsNone(abs_path)

    def test_css(self):
        abs_path = finders.find('blogango/css/as_blog_styles.css')
        self.assertIsNotNone(abs_path)
        abs_path = finders.find('blogango/css/prettify.css')
        self.assertIsNotNone(abs_path)
        abs_path = finders.find('logango/css/prettify.css')
        self.assertIsNone(abs_path)


class TestFeedUrl(TestCase):
    """Check different feed urls and if they are being set in the page"""
    def setUp(self):
        self.blog = Blog(title="test", tag_line="new blog", entries_per_page=10,
                    recents=5, recent_comments=5)
        self.blog.save()
        self.c = Client()
        self.user = User.objects.create_user(username='gonecrazy', email='gonecrazy@gmail.com', password='gonecrazy')

    def test_blog_feed(self):
        response = self.c.get(reverse("blogango_feed"))
        self.assertEqual(response.status_code, 200)

    def test_feed_url_on_index(self):
        response = self.c.get(reverse("blogango_feed"))
        self.assertGreater(response.content.find('/blog/rss/latest/'), 1)

def create_test_blog_entry(user):
    return BlogEntry.objects.create(**{'title': 'example post',
            'text': 'this is the test post',
            'publish_date': datetime.strptime("2011-09-22", "%Y-%m-%d"),
            'text_markup_type': "html",
            'created_by': user})


def create_test_comment(entry):
    Comment.objects.create(text="foo", comment_for=entry, is_public=True)




class TestCommentNotificationCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='gonecrazy', email='gonecrazy@gmail.com', password='gonecrazy')
        self.user.is_staff = True
        self.user.save()
        self.blog_entry = create_test_blog_entry(self.user)


    def test_comment_notify_sends_email(self):
        """Test if management command sends mail"""
        create_test_comment(self.blog_entry)
        self.assertEqual(len(mail.outbox), 0)
        call_command('comment_notify')
        self.assertEqual(len(mail.outbox), 1)

    def test_single_email_send_for_multiple_comments(self):
        """Test if a single mail send for multiple comments on a blong entry"""
        for each in range(5):
            create_test_comment(self.blog_entry)
        comments = Comment.objects.filter(comment_for=self.blog_entry)
        self.assertEqual(comments.count(), 5)
        self.assertEqual(len(mail.outbox), 0)
        call_command('comment_notify')
        self.assertEqual(len(mail.outbox), 1)

    def test_notification_for_muliple_posts(self):
        """Test if multiple mails are send for mulitiple blogs"""
        user2 = User.objects.create_user(username='testuser', email='testuser@gmail.com', password='testuser')
        user2.is_staff = True
        user2.save()
        blog_entry2 = create_test_blog_entry(user2)
        create_test_comment(self.blog_entry)
        create_test_comment(blog_entry2)
        self.assertEqual(len(mail.outbox), 0)
        call_command('comment_notify')
        self.assertEqual(len(mail.outbox), 2)
