# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class AlertMaster(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    production_day = models.CharField(max_length=45, blank=True)
    silo = models.CharField(db_column='SILO', max_length=45, blank=True)  # Field name made lowercase.
    server = models.CharField(db_column='Server', max_length=45, blank=True)  # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=20, blank=True)  # Field name made lowercase.
    service = models.CharField(db_column='Service', max_length=20, blank=True)  # Field name made lowercase.
    osm = models.CharField(db_column='OSM', max_length=20, blank=True)  # Field name made lowercase.
    pap = models.CharField(db_column='PAP', max_length=45, blank=True)  # Field name made lowercase.
    sla = models.CharField(db_column='SLA', max_length=45, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alert_master'


class AlertStatus(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    date = models.DateField(blank=True, null=True)
    silo = models.CharField(max_length=45, blank=True)
    sla_status = models.CharField(max_length=45, blank=True)
    delay_reason = models.CharField(max_length=100, blank=True)
    personnel = models.CharField(max_length=50, blank=True)
    class Meta:
        managed = False
        db_table = 'alert_status'


class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'


class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'


class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'


class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'


class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.IntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', blank=True, null=True)
    user = models.ForeignKey(AuthUser)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'


class DjangoMigrations(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoSite(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    domain = models.CharField(max_length=100)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'django_site'


class TaskOwner(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    task_owner = models.CharField(max_length=50, blank=True)

    class Meta:
        managed = False
        db_table = 'task_owner'


class TaskSum(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    retailer = models.CharField(max_length=45, blank=True)
    task = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=45, blank=True)
    weekday = models.CharField(max_length=45, blank=True)
    hub = models.CharField(max_length=45, blank=True)
    task_owner = models.CharField(max_length=80, blank=True)

    class Meta:
        managed = False
        db_table = 'task_sum'
