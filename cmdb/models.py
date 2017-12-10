# -*- coding: utf-8 -*-

from django.db import models


ASSET_STATUS = (
    (str(1), "使用中"),
    (str(2), "未使用"),
    (str(3), "故障"),
    (str(4), "其它"),
    )

ASSET_TYPE = (
    (str(1), "物理机"),
    (str(2), "虚拟机"),
    (str(3), "容器"),
    (str(4), "网络设备"),
    (str(5), "其他")
    )


class UserInfo(models.Model):
    username = models.CharField(max_length=30,null=True)
    password = models.CharField(max_length=30,null=True)

    def __str__(self):
        return self.username


class Idc(models.Model):
    name = models.CharField( max_length=30,null=True)
    address = models.CharField( max_length=100, null=True,blank=True)
    tel = models.CharField( max_length=30, null=True,blank=True)
    contact = models.CharField( max_length=30, null=True,blank=True)
    phone = models.CharField( max_length=30, null=True,blank=True)
    cabinet = models.CharField( max_length=30, null=True,blank=True)
    ip_range = models.CharField( max_length=30, null=True,blank=True)
    bandwidth = models.CharField(max_length=30, null=True,blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'idc'
        verbose_name_plural = verbose_name


class HostGroup(models.Model):
    name = models.CharField( max_length=30, unique=True)
    desc = models.CharField( max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class Host(models.Model):
    hostname = models.CharField(max_length=50, unique=True)
    ip = models.GenericIPAddressField( max_length=15)
    other_ip = models.CharField( max_length=100, null=True, blank=True)
    group = models.ForeignKey(HostGroup, on_delete=models.SET_NULL, null=True, blank=True)
    asset_no = models.CharField(max_length=50, null=True, blank=True)
    asset_type = models.CharField(choices=ASSET_TYPE, max_length=30, null=True, blank=True)
    status = models.CharField( choices=ASSET_STATUS, max_length=30, null=True, blank=True)
    os = models.CharField( max_length=100, null=True, blank=True)
    vendor = models.CharField( max_length=50, null=True, blank=True)
    cpu_model = models.CharField(max_length=100, null=True, blank=True)
    cpu_num = models.CharField( max_length=100, null=True, blank=True)
    memory = models.CharField( max_length=30, null=True, blank=True)
    disk = models.CharField( max_length=255, null=True, blank=True)
    sn = models.CharField( max_length=60, blank=True)
    idc = models.ForeignKey(Idc,  on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField( max_length=100, null=True, blank=True)
    memo = models.TextField( max_length=200, null=True, blank=True)

    def __str__(self):
        return self.hostname


class IpSource(models.Model):
    net = models.CharField(max_length=30)
    subnet = models.CharField(max_length=30,null=True)
    describe = models.CharField(max_length=30,null=True)

    def __str__(self):
        return self.net


class InterFace(models.Model):
    name = models.CharField(max_length=30)
    vendor = models.CharField(max_length=30,null=True)
    bandwidth = models.CharField(max_length=30,null=True)
    tel = models.CharField(max_length=30,null=True)
    contact = models.CharField(max_length=30,null=True)
    startdate = models.DateField()
    enddate = models.DateField()
    price = models.IntegerField()

    def __str__(self):
        return self.name
