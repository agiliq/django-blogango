
from django import template

register = template.Library()

from lib import ttp
    
@register.filter
def twitterify(tweet):
    parse = ttp.Parser()
    result = parse.parse(tweet)
    return result.html