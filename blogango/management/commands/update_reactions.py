from django.core.management.base import NoArgsCommand
from django.http import HttpRequest
from django.conf import settings

from blogango.models import BlogEntry, Reaction

import urllib2

try:
    import simplejson
except ImportError:
    import django.utils.simplejson

BACKTYPE_URL = "http://api.backtype.com/tweets/search/links.json?q=%s&key=%s"

class Command(NoArgsCommand):
    help = 'Sync reactions from backtype'

    def handle_noargs(self, **options):
        req = HttpRequest() # hack to get absolute uri for the blog entries
        for entry in BlogEntry.objects.all():
            entry_url = "http://agiliq.com/blog/2010/06/ubuntu-django-development-platform/" #req.build_absolute_uri(entry.get_absolute_url())
            url = BACKTYPE_URL %(entry_url, settings.BACKTYPE_API_KEY)
            resp = urllib2.urlopen(url)
            json_data = simplejson.load(resp)
            
            tweets = json_data["tweets"]
            for tweet in tweets:
                try:
                    reaction = Reaction.objects.get(pk=tweet['tweet_id'])
                except Reaction.DoesNotExist:
                    reaction = Reaction()
                    reaction.reaction_id = tweet['tweet_id']
                    reaction.comment_for = entry
                    reaction.created_on = tweet['tweet_created_at']
                    reaction.text = tweet['tweet_text']
                    reaction.user_name = tweet['tweet_from_user']
                    reaction.profile_image = tweet['tweet_profile_image_url']
                    reaction.source = "twitter"
                    reaction.save()
                    print "saved reaction %s from %s" %(tweet['tweet_text'], tweet['tweet_from_user'])