# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.db import models


class PingbackManager(models.Manager):
    def pingbacks_for_object(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=content_type, object_id=obj.pk)

    def count_for_object(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=content_type, object_id=obj.pk).count()


class PingbackClientManager(models.Manager):
    def count_for_link(self, obj, link):
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=ctype, object_id=obj.pk, url=link).count()
