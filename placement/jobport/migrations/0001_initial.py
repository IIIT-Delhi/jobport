# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Batch'
        db.create_table(u'jobport_batch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('createdon', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('pg_or_not', self.gf('django.db.models.fields.CharField')(default='G', max_length=1)),
        ))
        db.send_create_signal(u'jobport', ['Batch'])

        # Adding model 'Job'
        db.create_table(u'jobport_job', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('profile', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('dateofvisit', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('package', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('selectionprocess', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('jobtype', self.gf('django.db.models.fields.CharField')(default='T', max_length=2)),
            ('cgpa_min', self.gf('django.db.models.fields.FloatField')(default=1, max_length=2)),
            ('min_tenthmarks', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=3)),
            ('min_twelfthmarks', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=3)),
            ('max_blacklogs', self.gf('django.db.models.fields.IntegerField')(default=5, max_length=2)),
            ('status', self.gf('django.db.models.fields.CharField')(default='O', max_length=1)),
            ('jobfile', self.gf('django.db.models.fields.files.FileField')(default='', max_length=100, null=True, blank=True)),
            ('createdon', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'jobport', ['Job'])

        # Adding M2M table for field batch on 'Job'
        m2m_table_name = db.shorten_name(u'jobport_job_batch')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('job', models.ForeignKey(orm[u'jobport.job'], null=False)),
            ('batch', models.ForeignKey(orm[u'jobport.batch'], null=False))
        ))
        db.create_unique(m2m_table_name, ['job_id', 'batch_id'])

        # Adding model 'Student'
        db.create_table(u'jobport_student', (
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('rollno', self.gf('django.db.models.fields.CharField')(max_length=10, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('batch', self.gf('django.db.models.fields.related.ForeignKey')(related_name='studentsinbatch', to=orm['jobport.Batch'])),
            ('dob', self.gf('django.db.models.fields.DateTimeField')()),
            ('gender', self.gf('django.db.models.fields.CharField')(default='M', max_length=1)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=70)),
            ('email_personal', self.gf('django.db.models.fields.EmailField')(max_length=70, null=True, blank=True)),
            ('passingyear_tenth', self.gf('django.db.models.fields.IntegerField')(default=2009, max_length=4)),
            ('passingyear_twelfth', self.gf('django.db.models.fields.IntegerField')(default=2011, max_length=4)),
            ('percentage_tenth', self.gf('django.db.models.fields.FloatField')(max_length=4)),
            ('percentage_twelfth', self.gf('django.db.models.fields.FloatField')(max_length=4)),
            ('startyear', self.gf('django.db.models.fields.IntegerField')(default='2011', max_length=4)),
            ('passingyear', self.gf('django.db.models.fields.IntegerField')(default='2015', max_length=4)),
            ('university', self.gf('django.db.models.fields.CharField')(default='IIIT Delhi', max_length=100)),
            ('institution', self.gf('django.db.models.fields.CharField')(default='IIIT Delhi', max_length=100)),
            ('backlogs', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=2)),
            ('work_experience', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('home_city', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('home_state', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('credits_completed', self.gf('django.db.models.fields.CharField')(default=0, max_length=3, blank=True)),
            ('resume', self.gf('django.db.models.fields.files.FileField')(default='', max_length=100)),
            ('status', self.gf('django.db.models.fields.CharField')(default='N', max_length=1)),
        ))
        db.send_create_signal(u'jobport', ['Student'])

        # Adding M2M table for field companyapplications on 'Student'
        m2m_table_name = db.shorten_name(u'jobport_student_companyapplications')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('student', models.ForeignKey(orm[u'jobport.student'], null=False)),
            ('job', models.ForeignKey(orm[u'jobport.job'], null=False))
        ))
        db.create_unique(m2m_table_name, ['student_id', 'job_id'])

        # Adding M2M table for field placedat on 'Student'
        m2m_table_name = db.shorten_name(u'jobport_student_placedat')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('student', models.ForeignKey(orm[u'jobport.student'], null=False)),
            ('job', models.ForeignKey(orm[u'jobport.job'], null=False))
        ))
        db.create_unique(m2m_table_name, ['student_id', 'job_id'])

        # Adding model 'Feedback'
        db.create_table(u'jobport_feedback', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='C', max_length=1)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('createdon', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'jobport', ['Feedback'])


    def backwards(self, orm):
        # Deleting model 'Batch'
        db.delete_table(u'jobport_batch')

        # Deleting model 'Job'
        db.delete_table(u'jobport_job')

        # Removing M2M table for field batch on 'Job'
        db.delete_table(db.shorten_name(u'jobport_job_batch'))

        # Deleting model 'Student'
        db.delete_table(u'jobport_student')

        # Removing M2M table for field companyapplications on 'Student'
        db.delete_table(db.shorten_name(u'jobport_student_companyapplications'))

        # Removing M2M table for field placedat on 'Student'
        db.delete_table(db.shorten_name(u'jobport_student_placedat'))

        # Deleting model 'Feedback'
        db.delete_table(u'jobport_feedback')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'jobport.batch': {
            'Meta': {'object_name': 'Batch'},
            'createdon': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pg_or_not': ('django.db.models.fields.CharField', [], {'default': "'G'", 'max_length': '1'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'})
        },
        u'jobport.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'createdon': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'C'", 'max_length': '1'})
        },
        u'jobport.job': {
            'Meta': {'object_name': 'Job'},
            'batch': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'jobbatch'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['jobport.Batch']"}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'cgpa_min': ('django.db.models.fields.FloatField', [], {'default': '1', 'max_length': '2'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'createdon': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'dateofvisit': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'details': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jobfile': ('django.db.models.fields.files.FileField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'jobtype': ('django.db.models.fields.CharField', [], {'default': "'T'", 'max_length': '2'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'max_blacklogs': ('django.db.models.fields.IntegerField', [], {'default': '5', 'max_length': '2'}),
            'min_tenthmarks': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '3'}),
            'min_twelfthmarks': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '3'}),
            'package': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'profile': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'selectionprocess': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1'})
        },
        u'jobport.student': {
            'Meta': {'object_name': 'Student'},
            'backlogs': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2'}),
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'studentsinbatch'", 'to': u"orm['jobport.Batch']"}),
            'companyapplications': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'applicants'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['jobport.Job']"}),
            'credits_completed': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '3', 'blank': 'True'}),
            'dob': ('django.db.models.fields.DateTimeField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '70'}),
            'email_personal': ('django.db.models.fields.EmailField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'M'", 'max_length': '1'}),
            'home_city': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'home_state': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'institution': ('django.db.models.fields.CharField', [], {'default': "'IIIT Delhi'", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'passingyear': ('django.db.models.fields.IntegerField', [], {'default': "'2015'", 'max_length': '4'}),
            'passingyear_tenth': ('django.db.models.fields.IntegerField', [], {'default': '2009', 'max_length': '4'}),
            'passingyear_twelfth': ('django.db.models.fields.IntegerField', [], {'default': '2011', 'max_length': '4'}),
            'percentage_tenth': ('django.db.models.fields.FloatField', [], {'max_length': '4'}),
            'percentage_twelfth': ('django.db.models.fields.FloatField', [], {'max_length': '4'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'placedat': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'selectedcandidates'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['jobport.Job']"}),
            'resume': ('django.db.models.fields.files.FileField', [], {'default': "''", 'max_length': '100'}),
            'rollno': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'startyear': ('django.db.models.fields.IntegerField', [], {'default': "'2011'", 'max_length': '4'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'university': ('django.db.models.fields.CharField', [], {'default': "'IIIT Delhi'", 'max_length': '100'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'work_experience': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['jobport']