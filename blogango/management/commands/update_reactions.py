from django.core.management.base import NoArgsCommand
from django.http import HttpRequest
from django.conf import settings
from django.contrib.sites.models import Site

from blogango.models import BlogEntry, Reaction

import urllib2
import json


BACKTYPE_URL = "http://api.backtype.com/comments/connect.json?url=%s&key=%s"

class Command(NoArgsCommand):
    help = """
            Sync reactions from backtype
            
            Supports all sources from backtype
            Sample cron job call:
                python manage.py update_reactions
           """

    def handle_noargs(self, **options):
        current_site = Site.objects.get_current() # hack to get absolute uri for the blog entries
        for entry in BlogEntry.objects.all():
            entry_url = current_site.domain + entry.get_absolute_url()
            print "getting backtype results for %s" % (entry_url)
            url = BACKTYPE_URL % (entry_url, settings.BACKTYPE_API_KEY)
            resp = urllib2.urlopen(url)
            json_data = json.load(resp)            

            comments = json_data["comments"]
            for comment in comments:
                if comment['entry_type'] == 'tweet':
                    pk = comment['tweet_id']
                    created_on = comment['tweet_created_at']
                    text = comment['tweet_text']
                    user_name = comment['tweet_from_user']
                    profile_image = comment['tweet_profile_image_url']
                    user_url = "http://twitter.com/%s" %(user_name)
                    source = 'twitter'
                else:
                    pk = comment['comment']['id']
                    created_on = comment['comment']['date']
                    text = comment['comment']['content']
                    user_name = comment['author']['name']
                    user_url = comment['author']['url']
                    source = comment['entry_src']
                    if source == 'yc':
                        profile_image = "http://mediacdn.disqus.com/images/reactions/services/hackernews_128.png"
                    else:
                        profile_image = "http://mediacdn.disqus.com/images/reactions/services/%s_128.png" %(source)
                try:
                    reaction = Reaction.objects.get(pk=pk)
                except Reaction.DoesNotExist:
                    reaction = Reaction()
                    reaction.reaction_id = pk
                    reaction.comment_for = entry
                    reaction.created_on = created_on
                    reaction.text = text
                    reaction.user_name = user_name
                    reaction.user_url = user_url
                    reaction.profile_image = profile_image
                    reaction.source = source
                    reaction.save()

