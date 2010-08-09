# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BaseComment'
        db.create_table('blogango_basecomment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('comment_for', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['blogango.BlogEntry'], null=True, blank=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('blogango', ['BaseComment'])

        # Adding model 'Reaction'
        db.create_table('blogango_reaction', (
            ('basecomment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['blogango.BaseComment'], unique=True)),
            ('reaction_id', self.gf('django.db.models.fields.CharField')(max_length=200, primary_key=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('profile_image', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('blogango', ['Reaction'])

        # Deleting field 'Comment.created_on'
        db.delete_column('blogango_comment', 'created_on')

        # Deleting field 'Comment.user_name'
        db.delete_column('blogango_comment', 'user_name')

        # Deleting field 'Comment.text'
        db.delete_column('blogango_comment', 'text')

        # Deleting field 'Comment.comment_for'
        db.delete_column('blogango_comment', 'comment_for_id')

        # Deleting field 'Comment.id'
        db.delete_column('blogango_comment', 'id')

        # Adding field 'Comment.basecomment_ptr'
        db.add_column('blogango_comment', 'basecomment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(default=1, to=orm['blogango.BaseComment'], unique=True, primary_key=True), keep_default=False)

        # Adding field 'BlogEntry.text_markup_type'
        db.add_column('blogango_blogentry', 'text_markup_type', self.gf('django.db.models.fields.CharField')(default='markdown', max_length=30), keep_default=False)

        # Adding field 'BlogEntry._text_rendered'
        db.add_column('blogango_blogentry', '_text_rendered', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Changing field 'BlogEntry.text'
        db.alter_column('blogango_blogentry', 'text', self.gf('markupfield.fields.MarkupField')())


    def backwards(self, orm):
        
        # Deleting model 'BaseComment'
        db.delete_table('blogango_basecomment')

        # Deleting model 'Reaction'
        db.delete_table('blogango_reaction')

        # Adding field 'Comment.created_on'
        db.add_column('blogango_comment', 'created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2010, 8, 8, 5, 37, 16, 601276), blank=True), keep_default=False)

        # Adding field 'Comment.user_name'
        db.add_column('blogango_comment', 'user_name', self.gf('django.db.models.fields.CharField')(default='', max_length=100), keep_default=False)

        # Adding field 'Comment.text'
        db.add_column('blogango_comment', 'text', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Adding field 'Comment.comment_for'
        db.add_column('blogango_comment', 'comment_for', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['blogango.BlogEntry']), keep_default=False)

        # Adding field 'Comment.id'
        db.add_column('blogango_comment', 'id', self.gf('django.db.models.fields.AutoField')(default=1, primary_key=True), keep_default=False)

        # Deleting field 'Comment.basecomment_ptr'
        db.delete_column('blogango_comment', 'basecomment_ptr_id')

        # Deleting field 'BlogEntry.text_markup_type'
        db.delete_column('blogango_blogentry', 'text_markup_type')

        # Deleting field 'BlogEntry._text_rendered'
        db.delete_column('blogango_blogentry', '_text_rendered')

        # Changing field 'BlogEntry.text'
        db.alter_column('blogango_blogentry', 'text', self.gf('django.db.models.fields.TextField')())


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
        'blogango.basecomment': {
            'Meta': {'object_name': 'BaseComment'},
            'comment_for': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blogango.BlogEntry']", 'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
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
            'Meta': {'object_name': 'Comment', '_ormbases': ['blogango.BaseComment']},
            'basecomment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['blogango.BaseComment']", 'unique': 'True', 'primary_key': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'email_id': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'is_spam': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'user_url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'blogango.reaction': {
            'Meta': {'object_name': 'Reaction', '_ormbases': ['blogango.BaseComment']},
            'basecomment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['blogango.BaseComment']", 'unique': 'True'}),
            'profile_image': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'reaction_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
