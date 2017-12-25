#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.decorators import login_required

from .forms import IdcForm,addIdcForm
from .models import Idc


@login_required()
def idc(request):
    idc_info = Idc.objects.all()
    return render(request, 'cmdb/idc.html', locals())


@login_required()
def idc_add(request):
    if request.method == "POST":
        form = addIdcForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/cmdb/idc/")
        return render(request, "cmdb/idc_add.html", locals())
    else:
        form = addIdcForm()
        return render(request, "cmdb/idc_add.html", locals())


@login_required()
def idc_edit(request,id):
    obj=Idc.objects.get(id=id)
    if request.method == "POST":
        form=IdcForm(request.POST,instance=obj)
        if form.is_valid():
            form.save()
            return  redirect("/cmdb/idc/")
    else:
        form = IdcForm(instance=obj)
    return render(request,"cmdb/idc_edit.html",locals())

@login_required()
def idc_del(request):
    ret = {'status': True, 'error': None, 'data': None}
    if request.method == "POST":
        print(request.POST)
        try:
            id=request.POST.get("id")
            for i in json.loads(id):
                print(i)
                Idc.objects.get(id=int(i)).delete()
        except Exception as e:
            ret["error"] = str(e)
            ret["status"] = False
        return  HttpResponse(json.dumps(ret))


