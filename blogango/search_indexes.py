import datetime

from haystack import indexes
from blogango.models import BlogEntry


class BlogEntryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(model_attr='text',
                             document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    summary = indexes.CharField(model_attr='summary')
    created_by = indexes.CharField(model_attr='created_by')

    meta_keywords = indexes.CharField(model_attr='meta_keywords')
    meta_description = indexes.CharField(model_attr='meta_description')

    tags = indexes.CharField(model_attr='tags')

    def get_model(self):
        return BlogEntry

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(
            publish_date__lte=datetime.datetime.now())
