from datetime import datetime
from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.sites.models import Site


class Command(NoArgsCommand):
    """
        Send Notification email to blog author for recent(last 24hrs) comments.
    """
    author_mail_template_name = 'blogango/email/comment_notification.html'
    author_mail_subject = 'Comments to your Blog Posts'

    def handle_noargs(self, **options):
        users = User.objects.all()
        for user in users:
            if user.email:
                blog_with_comments = []
                blogs = user.blogentry_set.filter(is_published=True, publish_date__lte=datetime.now())
                for blog in blogs:
                    if blog.has_recent_comments():
                        blog_with_comments.append(blog)
                if blog_with_comments:
                    self.notify_author({
                        'user': user,
                        'blogs': blog_with_comments,
                        'current_site': Site.objects.get_current()
                    })

    def notify_author(self, data):
        message = render_to_string(self.author_mail_template_name, data)
        email = data['user'].email
        mail = EmailMessage(
            subject=self.author_mail_subject,
            body=message,
            from_email=settings.SERVER_EMAIL,
            to=[email],
        )
        mail.content_subtype = "html"
        mail.send()
