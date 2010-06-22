# -*- coding: utf-8 -*-

from datetime import datetime
from urlparse import urlsplit

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from pingback.managers import PingbackManager, PingbackClientManager


class Pingback(models.Model):
    url = models.URLField()
    date = models.DateTimeField(default=datetime.now)
    approved = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    content = models.TextField()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id')

    objects = PingbackManager()

    class Meta:
        db_table = 'pingback'
        ordering = ('-date', )

    def __unicode__(self):
        return u'%s to %s' % (self.url, self.object)

    def get_absolute_url(self):
        return object.get_absolute_url()

    def save(self):
        self.content = self.content.strip()
        super(Pingback, self).save()

    def get_host(self):
        return urlsplit(self.url)[1]

    # workaround for admin
    def admin_object(self):
        return self.object


class PingbackClient(models.Model):
    url = models.URLField()
    date = models.DateTimeField(default=datetime.now)
    success = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id')

    objects = PingbackClientManager()

    class Meta:
        db_table = 'pingback_client'
        ordering = ('-date', )

    def __unicode__(self):
        return u'%s to %s' % (self.object, self.url)

    # workaround for admin
    def admin_object(self):
        return self.object


class DirectoryPing(models.Model):
    url = models.URLField()
    date = models.DateTimeField(default=datetime.now)
    success = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id')

    objects = PingbackClientManager()

    class Meta:
        ordering = ('-date', )

    def __unicode__(self):
        return u'%s to %s' % (self.object, self.url)
