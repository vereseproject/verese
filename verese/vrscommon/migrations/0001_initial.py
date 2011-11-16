# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Relation'
        db.create_table('vrscommon_relation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user1', to=orm['auth.User'])),
            ('user2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user2', to=orm['auth.User'])),
            ('balance', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=7, decimal_places=2)),
            ('user1_trust_limit', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=2, blank=True)),
            ('user2_trust_limit', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=2, blank=True)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vrscommon.Currency'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('vrscommon', ['Relation'])

        # Adding unique constraint on 'Relation', fields ['user1', 'user2']
        db.create_unique('vrscommon_relation', ['user1_id', 'user2_id'])

        # Adding model 'Transaction'
        db.create_table('vrscommon_transaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vrscommon.Currency'])),
        ))
        db.send_create_signal('vrscommon', ['Transaction'])

        # Adding model 'Veresedaki'
        db.create_table('vrscommon_veresedaki', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ower', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2, blank=True)),
            ('local_amount', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['vrscommon.VeresedakiStatus'], unique=True, null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vrscommon.Transaction'])),
        ))
        db.send_create_signal('vrscommon', ['Veresedaki'])

        # Adding model 'VeresedakiStatus'
        db.create_table('vrscommon_veresedakistatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=30, blank=True)),
        ))
        db.send_create_signal('vrscommon', ['VeresedakiStatus'])

        # Adding model 'Currency'
        db.create_table('vrscommon_currency', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('symbol', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('rate', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=5)),
        ))
        db.send_create_signal('vrscommon', ['Currency'])

        # Adding model 'UserBalance'
        db.create_table('vrscommon_userbalance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vrscommon.Currency'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2)),
        ))
        db.send_create_signal('vrscommon', ['UserBalance'])

        # Adding unique constraint on 'UserBalance', fields ['user', 'currency']
        db.create_unique('vrscommon_userbalance', ['user_id', 'currency_id'])

        # Adding model 'UserProfile'
        db.create_table('vrscommon_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('pin', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vrscommon.Currency'])),
            ('wants_email', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('vrscommon', ['UserProfile'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'UserBalance', fields ['user', 'currency']
        db.delete_unique('vrscommon_userbalance', ['user_id', 'currency_id'])

        # Removing unique constraint on 'Relation', fields ['user1', 'user2']
        db.delete_unique('vrscommon_relation', ['user1_id', 'user2_id'])

        # Deleting model 'Relation'
        db.delete_table('vrscommon_relation')

        # Deleting model 'Transaction'
        db.delete_table('vrscommon_transaction')

        # Deleting model 'Veresedaki'
        db.delete_table('vrscommon_veresedaki')

        # Deleting model 'VeresedakiStatus'
        db.delete_table('vrscommon_veresedakistatus')

        # Deleting model 'Currency'
        db.delete_table('vrscommon_currency')

        # Deleting model 'UserBalance'
        db.delete_table('vrscommon_userbalance')

        # Deleting model 'UserProfile'
        db.delete_table('vrscommon_userprofile')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        },
        'vrscommon.currency': {
            'Meta': {'object_name': 'Currency'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '5'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'vrscommon.relation': {
            'Meta': {'unique_together': "(('user1', 'user2'),)", 'object_name': 'Relation'},
            'balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vrscommon.Currency']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user1'", 'to': "orm['auth.User']"}),
            'user1_trust_limit': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'user2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user2'", 'to': "orm['auth.User']"}),
            'user2_trust_limit': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'})
        },
        'vrscommon.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vrscommon.Currency']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'vrscommon.userbalance': {
            'Meta': {'unique_together': "(('user', 'currency'),)", 'object_name': 'UserBalance'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vrscommon.Currency']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'vrscommon.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vrscommon.Currency']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pin': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'wants_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'vrscommon.veresedaki': {
            'Meta': {'object_name': 'Veresedaki'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vrscommon.Transaction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'ower': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'status': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['vrscommon.VeresedakiStatus']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'vrscommon.veresedakistatus': {
            'Meta': {'object_name': 'VeresedakiStatus'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '30', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['vrscommon']
