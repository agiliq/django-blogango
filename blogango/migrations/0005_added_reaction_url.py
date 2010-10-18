# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Reaction.user_url'
        db.add_column('blogango_reaction', 'user_url', self.gf('django.db.models.fields.CharField')(default='', max_length=100), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Reaction.user_url'
        db.delete_column('blogango_reaction', 'user_url')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'blogango.blog': {
            'Meta': {'object_name': 'Blog'},
            'entries_per_page': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recent_comments': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'recents': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'tag_line': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'blogango.blogentry': {
            'Meta': {'object_name': 'BlogEntry'},
            '_text_rendered': ('django.db.models.fields.TextField', [], {}),
            'comments_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_page': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_rte': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'text': ('markupfield.fields.MarkupField', [], {}),
            'text_markup_type': ('django.db.models.fields.CharField', [], {'default': "'markdown'", 'max_length': '30'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'blogango.blogroll': {
            'Meta': {'object_name': 'BlogRoll'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        'blogango.comment': {
            'Meta': {'object_name': 'Comment'},
            'comment_for': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blogango.BlogEntry']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_id': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_spam': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user_url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'blogango.reaction': {
            'Meta': {'object_name': 'Reaction'},
            'comment_for': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blogango.BlogEntry']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'profile_image': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'reaction_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user_url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['blogango']
