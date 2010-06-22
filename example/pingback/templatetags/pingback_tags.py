#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2008 by Steingrim Dovland <steingrd@ifi.uio.no>

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.template import Library, Node, TemplateSyntaxError, Variable

from pingback.models import Pingback

register = Library()

class FillContextForObjectParser(object):
    def __call__(self, parser, token):
        tokens = token.split_contents()
        if len(tokens) != 5:
            raise TemplateSyntaxError, "%r tag requires 4 arguments" % tokens[0]
        if tokens[1] != 'for':
            raise TemplateSyntaxError, "First argument in %r tag must be 'for'" % tokens[0]
        if tokens[3] != 'as':
            raise TemplateSyntaxError, "Third argument in %r tag must be 'as'" % tokens[0]
        object_variable = tokens[2]
        context_variable = tokens[4]
        return self.do_tag(object_variable, context_variable)


class PingbackBaseNode(Node):
    def __init__(self, object_variable, context_variable):
        self.context_variable = context_variable
        self.object_variable = Variable(object_variable)


class PingbackListNode(PingbackBaseNode):
    def render(self, context):
        obj = self.object_variable.resolve(context)
        context[self.context_variable] = Pingback.objects.pingbacks_for_object(obj)
        return ''


class DoPingbackList(FillContextForObjectParser):
    """
    Gets list of Pingback objects for then given parameter and populates
    the context with a variable containing that list. The variable's
    name is defined by the `as` clause of the tag.

    Syntax::

        {% get_pingback_list for [context_var_containing_obj] as [varname] %}

    Example usage::

        {% get_pingback_list for object as pingback_list %}

    """
    def do_tag(self, object_variable, context_variable):
        return PingbackListNode(object_variable, context_variable)


class PingbackCountNode(PingbackBaseNode):
    def render(self, context):
        obj = self.object_variable.resolve(context)
        context[self.context_variable] = Pingback.objects.count_for_object(obj)
        return ''


class DoPingbackCount(FillContextForObjectParser):
    """
    Gets pingback count for the given params and populates the template
    context with a variable containing that value. The variable's name
    is defined by the `as` clause of the tag.

    Syntax::

        {% get_pingback_count for [context_var_containing_obj] as [varname] %}

    Example usage::

        {% get_pingback_count for object as pingback_count %}

    """
    def do_tag(self, object_variable, context_variable):
        return PingbackCountNode(object_variable, context_variable)


register.tag("get_pingback_count", DoPingbackCount())
register.tag("get_pingback_list", DoPingbackList())
