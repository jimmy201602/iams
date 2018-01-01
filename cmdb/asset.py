#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import datetime
import json

from django.shortcuts import render, HttpResponse,redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from cmdb.api import get_object,get_verbose_name,paginate_queryset
#from config.views import get_dir
#from config.config_api import  Config
from .forms import AssetForm,addAssetForm
from .models import Host, Idc, HostGroup, ASSET_STATUS, ASSET_TYPE
#from accounts.models import  UserInfo




@login_required()
def asset(request):
    #print(request.GET)
    #webssh_domain = Config.webssh()["webssh_domain"]
    asset_data = []
    idc_info = Idc.objects.all()
    host_list = Host.objects.all()
    group_info = HostGroup.objects.all()
    asset_types = ASSET_TYPE
    asset_status = ASSET_STATUS
    idc_name = request.GET.get('idc', None)
    group_name = request.GET.get('group', None)
    asset_type = request.GET.get('asset_type', None)
    status = request.GET.get('status', None)
    keyword = request.GET.get('keyword', None)
    export = request.GET.get("export", None)
    group_id = request.GET.get("group_id", None)
    idc_id = request.GET.get("idc_id", None)
    asset_id_all = request.GET.getlist("id", None)
    if keyword:
        keyword=keyword.strip()
        asset_data = Host.objects.filter(
            Q(hostname__contains=keyword) |
            Q(ip__contains=keyword) |
            Q(other_ip__contains=keyword) |
            Q(os__contains=keyword) |
            Q(vendor__contains=keyword) |
            Q(cpu_model__contains=keyword) |
            Q(cpu_num__contains=keyword) |
            Q(memory__contains=keyword) |
            Q(disk__contains=keyword) |
            Q(sn__contains=keyword) |
            Q(position__contains=keyword) |
            Q(memo__contains=keyword)    |
            Q(group__name=keyword) |
            Q(idc__name=keyword)
        )
    else:
        asset_data=Host.objects.all()

    page_no = int(request.GET.get("page_no", "1"))
    data, pagination_data = paginate_queryset(asset_data, page_no)
    return render(request, 'asset.html', locals())




@login_required()
def export(request):
    response = HttpResponse(content_type='text/csv')
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = now + '.csv'
    id_data=request.GET.get("id",None)
    id_list=json.loads(id_data)
    response['Content-Disposition'] = "attachment; filename=" + file_name
    if id_list:
        asset_find=[ Host.objects.filter(id=int(id)) for id in id_list ]
        writer = csv.writer(response)
        writer.writerow(get_verbose_name("cmdb", "Host"))
        for i in asset_find:
            for h in i:
                writer.writerow([h.hostname, h.ip,h.port, h.other_ip, h.group, h.asset_no,h.get_asset_type_display(), h.get_status_display(), h.os, h.vendor,h.cpu_model, h.cpu_num,h.memory, h.disk,h.sn,h.idc,h.position, h.memo])
        return response
    else:
        host = Host.objects.all()
        writer = csv.writer(response)
        writer.writerow(get_verbose_name("cmdb","Host"))
        for h in list(host):
            writer.writerow([h.hostname, h.ip, h.port, h.other_ip, h.group, h.asset_no, h.get_asset_type_display(),h.get_status_display(), h.os, h.vendor, h.cpu_model,h.cpu_num, h.memory, h.disk, h.sn, h.idc, h.position, h.memo])
        return response


@login_required()
def asset_add(request):
    if request.method == "POST":
        form = addAssetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/cmdb/asset/")
        return render(request, "asset_add.html", locals())
    else:
        form = addAssetForm()
        return render(request, "asset_add.html", locals())


@login_required()
def asset_edit(request,id):
    obj=Host.objects.get(id=id)
    if request.method == "POST":
        form=AssetForm(request.POST,instance=obj)
        if form.is_valid():
            form.save()
            return  redirect("/cmdb/asset/")
        return render(request, "asset_edit.html", locals())
    else:
        form = AssetForm(instance=obj)
    return render(request,"asset_edit.html",locals())


@login_required()
def asset_del(request):
    ret = {'status': True, 'error': None, 'data': None}
    if request.method == "POST":
        #print(request.POST)
        try:
            id=request.POST.get("id")
            for i in json.loads(id):
                #print(i)
                Host.objects.get(id=int(i)).delete()
        except Exception as e:
            ret["error"] = str(e)
            ret["status"] = False
        return  HttpResponse(json.dumps(ret))

