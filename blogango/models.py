from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User

class Blog(models.Model):
     """Blog wide settings.
     title:title of the Blog.
     tag_line: Tagline/subtitle of the blog. This two are genearlly displayed on each page's header.
     entries_per_page=Number of entries to display on each page.
     recents: Number of recent entries to display in the sidebar.
     recent_comments: Number of recent comments to display in the sidebar.
     """

     title = models.CharField(max_length = 100)
     tag_line = models.CharField(max_length = 100)
     entries_per_page = models.IntegerField(default = 10)
     recents = models.IntegerField(default = 5)
     recent_comments = models.IntegerField(default = 5)
     def __str__ (self):
        return self.title
     class Admin:
         pass
     def save (self):
        """There should not be more than one Blog object"""
        if Blog.objects.count() > 1 and self.id:
           raise Exception("Only one blog object allowed.")
        super(Blog, self).save() # Call the "real" save() method.

        

class BlogEntry(models.Model):
    """Each blog entry.
    Title: Post title.
    Slug: Post slug. These two if not given are inferred directly from entry text.
    text = The main data for the post.
    summary = The summary for the text. probably can can be derived from text, bit we dont want do do that each time main page is displayed.
    created_on = The date this entry was created. Defaults to now.
    Created by: The user who wrote this.
    is_page: IS this a page or a post? Pages are the more important posts, which might be displayed differently. Defaults to false.
    is_published: Is this page published. If yes then we would display this on site, otherwise no. Default to true.
    comments_allowed: Are comments allowed on this post? Default to True
    is_rte: Was this post done using a Rich text editor?"""
    
    title = models.CharField(max_length = 100)
    slug = models.CharField(max_length = 100)
    text = models.TextField()
    summary = models.TextField()
    created_on = models.DateTimeField(auto_now_add = True)
    created_by = models.ForeignKey(User, unique = False)
    is_page = models.BooleanField(default = False)
    is_published = models.BooleanField(default = True)
    comments_allowed = models.BooleanField(default = True)
    is_rte = models.BooleanField(default = False)
    
    meta_keywords = models.TextField(blank = True, null = True)
    meta_description = models.TextField(blank = True, null = True)

    @permalink
    def get_absolute_url (self):
          #return '/details/%s/' %self.id
          return ('blogango.views.details', [self.id])
    
    @permalink 
    def get_edit_url (self):
        #return '/edit/%s/' %self.id
          return ('blogango.views.edit_entry', [self.id])
     
    def get_num_comments (self):
        cmnt_count = Comment.objects.filter(comment_for = self).count()
        return cmnt_count
        
        
    def save (self):
        if self.title == None  or self.title == '':
           self.title = _infer_title_or_slug(self.text)
        if self.slug == None or self.slug == '':
           self.slug = _infer_title_or_slug(self.text)
        self.summary = _generate_summary(self.text)
        if not self.meta_keywords:
           self.meta_keywords = self.summary
        if not self.meta_description:
           self.meta_description = self.summary
         
        super(BlogEntry, self).save() # Call the "real" save() method.
        
    def __str__ (self):
        return self.title
        
    class Admin:
       pass
    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'Blog entries'

class Comment(models.Model):
    """Comments for each blog.
    text: The comment text.
    comment_for: the Post/Page this comment is created for.
    created_on: The date this comment was written on.
    created_by: THe user who wrote this comment.
    user_name = If created_by is null, this comment was by anonymous user. Name in that case.
    email_id: Email-id, as in user_name.
    is_spam: Is comment marked as spam? We do not display the comment in those cases."""
    text = models.TextField()
    comment_for = models.ForeignKey(BlogEntry)
    created_on = models.DateTimeField(auto_now_add = True)
    created_by = models.ForeignKey(User, unique = False, blank = True)
    user_name = models.CharField(max_length = 100)
    email_id = models.EmailField()
    is_spam = models.BooleanField(default = False)
    
    @permalink
    def get_absolute_url (self):
        #return '/comment/%s/' %self.id
          return ('comment_details', self.id)
     
    def __str__(self):
        return self.text
    class Admin:
       pass
    class Meta:
        ordering = ['created_on']
        
    

class Tag(models.Model):
    """Blog-entry tagged as.
    tag_txt: what is this tagged as?
    tag_for: The entry for which the tag is created.
    created_on: When was this tag created; Default to now."""
    tag_txt = models.CharField(max_length = 100, unique = True)
    tag_for = models.ManyToManyField(BlogEntry)
    created_on = models.DateTimeField(auto_now_add = True)
    def get_absolute_url (self):
        return '/tag/%s/' %self.tag_txt
    def __str__(self):
        return self.tag_txt
    class Admin:
       pass
    class Meta:
        ordering = ['-created_on']


class BlogRoll(models.Model):
      url = models.URLField(unique = True)
      text = models.CharField(max_length = 100)
      is_published = models.BooleanField(default = True)
      def get_absolute_url (self):
        return '%s' %self.url
      class Admin:
         pass
        
        
        
#Helper methods
def _infer_title_or_slug (text):
    title = '-'.join(text.split()[:5])
    return title

def _generate_summary (text):
     summary = text.split()[:100]
     summary = ' '.join(summary)
     return summary
        


        
