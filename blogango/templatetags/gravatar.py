### gravatar.py ###############
# place inside a 'templatetags' directory inside the top level of a Django app (not project, must be inside an app)
# at the top of your page template include this:
# {% load gravatar %}
# and to use the url do this:
# <img src="{% gravatar_url 'someone@somewhere.com' %}"/>
# or
# <img src="{% gravatar_url sometemplatevariable %}"/>
# just make sure to update the "default" image path below

import urllib
import hashlib

from django import template

register = template.Library()


class GravatarUrlNode(template.Node):

    def __init__(self, email):
        self.email = template.Variable(email)

    def render(self, context):
        try:
            email = self.email.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        default = "http://www.gravatar.com/avatar"
        size = 50

        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'default': default, 'size': str(size)})

        return gravatar_url


@register.tag
def gravatar_url(parser, token):
    try:
        tag_name, email = token.split_contents()

    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    return GravatarUrlNode(email)
