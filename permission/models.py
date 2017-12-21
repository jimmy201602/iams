# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Permission(models.Model):
    name = models.CharField(max_length=50,verbose_name="Name",unique=True,blank=False)
    app = models.CharField(max_length=50,verbose_name="App",unique=True,blank=False)
    model = models.CharField(max_length=50,verbose_name="Model",unique=True,blank=False)
    description = models.TextField(verbose_name="Description",blank=True)
    createtime = models.DateTimeField(verbose_name='Create time',auto_now_add=True,editable=False)
    updatetime = models.DateTimeField(verbose_name='Update time',auto_now=True,editable=True)
    
    def __unicode__(self):
        return self.name
    
class Role(models.Model):
    name = models.CharField(max_length=50,verbose_name="Name",unique=True,blank=False)
    description = models.TextField(verbose_name="Description",blank=True)
    createtime = models.DateTimeField(verbose_name='Create time',auto_now_add=True,editable=False)
    updatetime = models.DateTimeField(verbose_name='Update time',auto_now=True,editable=True)
    
    def __unicode__(self):
        return self.name
    
class RolePermission(models.Model):
    name = models.ForeignKey(Role)
    permission = models.ManyToManyField(Permission)
    createtime = models.DateTimeField(verbose_name='Create time',auto_now_add=True,editable=False)
    updatetime = models.DateTimeField(verbose_name='Update time',auto_now=True,editable=True)
    
    def __unicode__(self):
        return self.name.name

class RoleMember(models.Model):
    name = models.ForeignKey(Role)
    member = models.ManyToManyField(Permission)
    createtime = models.DateTimeField(verbose_name='Create time',auto_now_add=True,editable=False)
    updatetime = models.DateTimeField(verbose_name='Update time',auto_now=True,editable=True)
    
    def __unicode__(self):
        return self.name.name

class PermissionList(models.Model):
    name = models.CharField(max_length=50,verbose_name="App Name",unique=True,blank=False)
    permissions = models.ManyToManyField(Permission)
    createtime = models.DateTimeField(verbose_name='Create time',auto_now_add=True,editable=False)
    updatetime = models.DateTimeField(verbose_name='Update time',auto_now=True,editable=True)
    
    def __unicode__(self):
        return self.name    