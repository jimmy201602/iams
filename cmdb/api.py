#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging


from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from .models import Host,HostGroup
#from .models import Host, HostGroup, ASSET_TYPE, ASSET_STATUS


#from api.common import token_verify
#from api.deploy_key import deploy_key
#from api.log import log
#from config.config_api import Config
#from config.views import get_dir




def get_verbose_name(appname,modelname,exclude=["id"]):
    modelobj=apps.get_model(appname,modelname)
    filed= modelobj._meta.fields
    params=[ f for f in filed if f.name not in exclude]
    result=[ i.verbose_name for i in params ]
    return result



##分页功能
def paginate_queryset(objs,page_no,cnt_per_page=20,half_show_length=5):
    p = Paginator(objs,cnt_per_page)
    if page_no > p.num_pages:
        page_no = p.num_pages
    if page_no <= 0:
        page_no =1
    page_links = [ i for i in range(page_no - half_show_length,page_no + half_show_length +1 )
                   if i>0 and i <= p.num_pages]
    page = p.page(page_no)
    previous_link = page_links[0] -1
    next_link = page_links[-1] +1
    pagination_data = {
        "has_previous": previous_link >0,
        "has_next" :next_link <= p.num_pages,
        "previous_link":previous_link,
        "next_link":next_link,
        "page_cnt":p.num_pages,
        "current_no":page_no,
        "page_links":page_links
    }
    return (page.object_list,pagination_data)


def get_object(model, **kwargs):
    """
    use this function for query
    使用改封装函数查询数据库
    """
    for value in kwargs.values():
        if not value:
            return None

    the_object = model.objects.filter(**kwargs)
    if len(the_object) == 1:
        the_object = the_object[0]
    else:
        the_object = None
    return the_object


def page_list_return(total, current=1):
    """
    page
    分页，返回本次分页的最小页数到最大页数列表
    """
    min_page = current - 2 if current - 4 > 0 else 1
    max_page = min_page + 4 if min_page + 4 < total else total

    return range(min_page, max_page + 1)





@csrf_exempt
#@token_verify()
def collect(request):
    asset_info = json.loads(request.body)
    if request.method == 'POST':
        vendor = asset_info['vendor']
        # group = asset_info['group']
        disk = asset_info['disk']
        cpu_model = asset_info['cpu_model']
        cpu_num = asset_info['cpu_num']
        memory = asset_info['memory']
        sn = asset_info['sn']
        osver = asset_info['osver']
        hostname = asset_info['hostname']
        ip = asset_info['ip']
        # asset_type = ""
        # status = ""
        try:
            host = Host.objects.get(hostname=hostname)
        except Exception as msg:
            print(msg)
            host = Host()
            # level = Config.conf()["log_level"]
            # ssh_pwd = Config.webssh()["ssh_pwd"]
            # log_path = Config.conf()["log_path"]
            # log("cmdb.log", level, log_path)
            # logging.info("==========sshkey deploy start==========")
            # data = deploy_key(ip, ssh_pwd)
            # logging.info(data)
            # logging.info("==========sshkey deploy end==========")

        # if req.POST.get('identity'):
        #     identity = req.POST.get('identity')
        #     try:
        #         host = Host.objects.get(identity=identity)
        #     except:
        #         host = Host()
        host.hostname = hostname
        # host.group = group
        host.cpu_num = int(cpu_num)
        host.cpu_model = cpu_model
        host.memory = int(memory)
        host.sn = sn
        host.disk = disk
        host.os = osver
        host.vendor = vendor
        host.ip = ip
        # host.asset_type = asset_type
        # host.status = status
        host.save()
        return HttpResponse("Post asset data to server successfully!")
    else:
        return HttpResponse("No any post data!")


#@token_verify()
def get_host(request):
    d = []
    try:
        hostname = request.GET['name']
    except Exception as msg:
        return HttpResponse(msg, status=404)
    if hostname == "all":
        all_host = Host.objects.all()
        ret_host = {'hostname': hostname, 'members': []}
        for h in all_host:
            ret_h = {'hostname': h.hostname, 'ipaddr': h.ip}
            ret_host['members'].append(ret_h)
        d.append(ret_host)
        return HttpResponse(json.dumps(d))
    else:
        try:
            host = Host.objects.get(hostname=hostname)
            data = {'hostname': host.hostname, 'ip': host.ip}
            return HttpResponse(json.dumps({'status': 0, 'message': 'ok', 'data': data}))
        except Exception as msg:
            return HttpResponse(msg, status=404)


#@token_verify()
def get_group(request):
    if request.method == 'GET':
        d = []
        try:
            group_name = request.GET['name']
        except Exception as msg:
            return HttpResponse(msg)
        if group_name == "all":
            host_groups = HostGroup.objects.all()
            for hg in host_groups:
                ret_hg = {'host_group': hg.name, 'members': []}
                members = Host.objects.filter(group__name=hg)
                for h in members:
                    ret_h = {'hostname': h.hostname, 'ipaddr': h.ip}
                    ret_hg['members'].append(ret_h)
                d.append(ret_hg)
            return HttpResponse(json.dumps(d))
        else:
            ret_hg = {'host_group': group_name, 'members': []}
            members = Host.objects.filter(group__name=group_name)
            for h in members:
                ret_h = {'hostname': h.hostname, 'ipaddr': h.ip}
                ret_hg['members'].append(ret_h)
            d.append(ret_hg)
            return HttpResponse(json.dumps(d))
    return HttpResponse(status=403)