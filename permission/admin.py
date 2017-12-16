# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from cmdb.models import Category,Characteristic,CharacteristicValue,Equipment

admin.site.register(Category)
admin.site.register(Characteristic)
admin.site.register(Equipment)
admin.site.register(CharacteristicValue)