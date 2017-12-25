#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Host, HostGroup
from .forms import GroupForm, AssetForm


@login_required()
def group(request):
    allgroup = HostGroup.objects.all()
    return render(request, 'cmdb/group.html', locals())


@login_required()
def group_add(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            return redirect("/cmdb/group/")
        return render(request, "cmdb/group_add.html", locals())
    else:
        form = GroupForm()
        return render(request, "cmdb/group_add.html", locals())


@login_required()
def group_edit(request, id):
    obj = HostGroup.objects.get(id=id)
    #allgroup = HostGroup.objects.all()
    unselect = Host.objects.filter(group__name=None)
    members = Host.objects.filter(group__name=obj.name)
    return render(request, "cmdb/group_edit.html", locals())

@login_required()
def group_edit_new(request,id):
    obj=HostGroup.objects.get(id=id)
    if request.method == "POST":
        form=GroupForm(request.POST,instance=obj)
        if form.is_valid():
            form.save()
            return  redirect("/cmdb/group/")
    else:
        form = GroupForm(instance=obj)
        unselect=AssetForm()
    return render(request,"cmdb/group_edit.html",locals())

@login_required()
def group_del(request):
    ret = {'status': True, 'error': None, 'data': None}
    if request.method == "POST":
        print(request.POST)
        try:
            id=request.POST.get("id")
            for i in json.loads(id):
                print(i)
                HostGroup.objects.get(id=int(i)).delete()
        except Exception as e:
            ret["error"] = str(e)
            ret["status"] = False
        return  HttpResponse(json.dumps(ret))






@login_required()
def group_save(request):
    if request.method == 'POST':
        group_id = request.POST.get('id')
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        members = request.POST.getlist('members', [])
        unselect = request.POST.getlist('unselect', [])
        group_item = HostGroup.objects.get(id=group_id)
        if unselect:
            for host in unselect:
                # print "unselect: "+host
                obj = Host.objects.get(hostname=host)
                obj.group_id = None
                obj.save()
        if members:
            for host in members:
                # print "members: "+host
                obj = Host.objects.get(hostname=host)
                obj.group_id = group_id
                obj.save()
        group_item.name = name
        group_item.desc = desc
        group_item.save()
        obj = group_item
        status = 1
        return redirect("/cmdb/group/")
    else:
        status = 2
    return render(request, "cmdb/group_edit.html", locals())
