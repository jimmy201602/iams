# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from permission.models import Permission,Role,RolePermission,RoleMember,PermissionList
from django import forms

class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        widgets = {
        'app': forms.Select(choices=[(data['app_label'],data['app_label']) for data in ContentType.objects.values('app_label').distinct()]),
        'model':forms.Select(choices=[(data.model,data.model) for data in ContentType.objects.all()]),
        }
        fields = '__all__'

class PermissionAdmin(admin.ModelAdmin):
    form = PermissionForm
    
admin.site.register(Permission,PermissionAdmin)
admin.site.register(Role)
admin.site.register(RolePermission)
admin.site.register(RoleMember)
admin.site.register(PermissionList)