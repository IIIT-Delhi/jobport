# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Student.passingyear'
        db.delete_column(u'jobport_student', 'passingyear')

        # Deleting field 'Student.startyear'
        db.delete_column(u'jobport_student', 'startyear')

        # Deleting field 'Student.institution'
        db.delete_column(u'jobport_student', 'institution')

        # Deleting field 'Student.university'
        db.delete_column(u'jobport_student', 'university')

        # Deleting field 'Student.cgpa'
        db.delete_column(u'jobport_student', 'cgpa')

        # Adding field 'Student.cgpa_ug'
        db.add_column(u'jobport_student', 'cgpa_ug',
                      self.gf('django.db.models.fields.FloatField')(default=0, max_length=4),
                      keep_default=False)

        # Adding field 'Student.cgpa_pg'
        db.add_column(u'jobport_student', 'cgpa_pg',
                      self.gf('django.db.models.fields.FloatField')(default=0, max_length=4),
                      keep_default=False)

        # Adding field 'Student.startyear_ug'
        db.add_column(u'jobport_student', 'startyear_ug',
                      self.gf('django.db.models.fields.IntegerField')(default='2011', max_length=4),
                      keep_default=False)

        # Adding field 'Student.passingyear_ug'
        db.add_column(u'jobport_student', 'passingyear_ug',
                      self.gf('django.db.models.fields.IntegerField')(default='2015', max_length=4),
                      keep_default=False)

        # Adding field 'Student.university_ug'
        db.add_column(u'jobport_student', 'university_ug',
                      self.gf('django.db.models.fields.CharField')(default='IIIT Delhi', max_length=100),
                      keep_default=False)

        # Adding field 'Student.institution_ug'
        db.add_column(u'jobport_student', 'institution_ug',
                      self.gf('django.db.models.fields.CharField')(default='IIIT Delhi', max_length=100),
                      keep_default=False)

        # Adding field 'Student.startyear_pg'
        db.add_column(u'jobport_student', 'startyear_pg',
                      self.gf('django.db.models.fields.IntegerField')(default='2011', max_length=4),
                      keep_default=False)

        # Adding field 'Student.passingyear_pg'
        db.add_column(u'jobport_student', 'passingyear_pg',
                      self.gf('django.db.models.fields.IntegerField')(default='2015', max_length=4),
                      keep_default=False)

        # Adding field 'Student.university_pg'
        db.add_column(u'jobport_student', 'university_pg',
                      self.gf('django.db.models.fields.CharField')(default='IIIT Delhi', max_length=100),
                      keep_default=False)

        # Adding field 'Student.institution_pg'
        db.add_column(u'jobport_student', 'institution_pg',
                      self.gf('django.db.models.fields.CharField')(default='IIIT Delhi', max_length=100),
                      keep_default=False)


        # Changing field 'Student.work_experience'
        db.alter_column(u'jobport_student', 'work_experience', self.gf('django.db.models.fields.IntegerField')(max_length=2))

    def backwards(self, orm):
        # Adding field 'Student.passingyear'
        db.add_column(u'jobport_student', 'passingyear',
                      self.gf('django.db.models.fields.IntegerField')(default='2015', max_length=4),
                      keep_default=False)

        # Adding field 'Student.startyear'
        db.add_column(u'jobport_student', 'startyear',
                      self.gf('django.db.models.fields.IntegerField')(default='2011', max_length=4),
                      keep_default=False)

        # Adding field 'Student.institution'
        db.add_column(u'jobport_student', 'institution',
                      self.gf('django.db.models.fields.CharField')(default='IIIT Delhi', max_length=100),
                      keep_default=False)

        # Adding field 'Student.university'
        db.add_column(u'jobport_student', 'university',
                      self.gf('django.db.models.fields.CharField')(default='IIIT Delhi', max_length=100),
                      keep_default=False)

        # Adding field 'Student.cgpa'
        db.add_column(u'jobport_student', 'cgpa',
                      self.gf('django.db.models.fields.FloatField')(default=4, max_length=4),
                      keep_default=False)

        # Deleting field 'Student.cgpa_ug'
        db.delete_column(u'jobport_student', 'cgpa_ug')

        # Deleting field 'Student.cgpa_pg'
        db.delete_column(u'jobport_student', 'cgpa_pg')

        # Deleting field 'Student.startyear_ug'
        db.delete_column(u'jobport_student', 'startyear_ug')

        # Deleting field 'Student.passingyear_ug'
        db.delete_column(u'jobport_student', 'passingyear_ug')

        # Deleting field 'Student.university_ug'
        db.delete_column(u'jobport_student', 'university_ug')

        # Deleting field 'Student.institution_ug'
        db.delete_column(u'jobport_student', 'institution_ug')

        # Deleting field 'Student.startyear_pg'
        db.delete_column(u'jobport_student', 'startyear_pg')

        # Deleting field 'Student.passingyear_pg'
        db.delete_column(u'jobport_student', 'passingyear_pg')

        # Deleting field 'Student.university_pg'
        db.delete_column(u'jobport_student', 'university_pg')

        # Deleting field 'Student.institution_pg'
        db.delete_column(u'jobport_student', 'institution_pg')


        # Changing field 'Student.work_experience'
        db.alter_column(u'jobport_student', 'work_experience', self.gf('django.db.models.fields.CharField')(max_length=20))

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
            'cgpa_pg': ('django.db.models.fields.FloatField', [], {'default': '0', 'max_length': '4'}),
            'cgpa_ug': ('django.db.models.fields.FloatField', [], {'default': '0', 'max_length': '4'}),
            'companyapplications': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'applicants'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['jobport.Job']"}),
            'credits_completed': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '3', 'blank': 'True'}),
            'dob': ('django.db.models.fields.DateTimeField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '70'}),
            'email_personal': ('django.db.models.fields.EmailField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'M'", 'max_length': '1'}),
            'home_city': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'home_state': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'institution_pg': ('django.db.models.fields.CharField', [], {'default': "'IIIT Delhi'", 'max_length': '100'}),
            'institution_ug': ('django.db.models.fields.CharField', [], {'default': "'IIIT Delhi'", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'passingyear_pg': ('django.db.models.fields.IntegerField', [], {'default': "'2015'", 'max_length': '4'}),
            'passingyear_tenth': ('django.db.models.fields.IntegerField', [], {'default': '2009', 'max_length': '4'}),
            'passingyear_twelfth': ('django.db.models.fields.IntegerField', [], {'default': '2011', 'max_length': '4'}),
            'passingyear_ug': ('django.db.models.fields.IntegerField', [], {'default': "'2015'", 'max_length': '4'}),
            'percentage_tenth': ('django.db.models.fields.FloatField', [], {'max_length': '4'}),
            'percentage_twelfth': ('django.db.models.fields.FloatField', [], {'max_length': '4'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'placedat': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'selectedcandidates'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['jobport.Job']"}),
            'resume': ('django.db.models.fields.files.FileField', [], {'default': "''", 'max_length': '100'}),
            'rollno': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'startyear_pg': ('django.db.models.fields.IntegerField', [], {'default': "'2011'", 'max_length': '4'}),
            'startyear_ug': ('django.db.models.fields.IntegerField', [], {'default': "'2011'", 'max_length': '4'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'university_pg': ('django.db.models.fields.CharField', [], {'default': "'IIIT Delhi'", 'max_length': '100'}),
            'university_ug': ('django.db.models.fields.CharField', [], {'default': "'IIIT Delhi'", 'max_length': '100'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'work_experience': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2'})
        }
    }

    complete_apps = ['jobport']