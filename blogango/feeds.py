from django.contrib.syndication.feeds import Feed
from models import *

class main_feed (Feed):
    try:
       blog = Blog.objects.all()[0]
    except:
       class DummyBlog:
           def __init__ (self):         
             self.title = ''
             self.tag_line = ''
       blog = DummyBlog()
    title = blog.title
    link = "/rss/latest/"
    description = blog.tag_line
    def items (self):
       entries = BlogEntry.objects.all()[:10]
       return entries
    
class CatFeed(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Tag.objects.get(tag_txt__exact=bits[0])
    
    def title(self, obj):
        return "%s" % obj.tag_txt
    
    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()
    
    def description(self, obj):
        return "Category: %s" % obj.tag_txt
    
    def items(self, obj):
        return obj.tag_for.filter(is_published = True)