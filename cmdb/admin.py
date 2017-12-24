from django.contrib import admin

# Register your models here.
from cmdb.models import Category,Characteristic,CharacteristicValue,Equipment,Host,HostGroup,Idc

admin.site.register(Category)
admin.site.register(Characteristic)
admin.site.register(Equipment)
admin.site.register(CharacteristicValue)
admin.site.register(Host)
admin.site.register(HostGroup)
admin.site.register(Idc)