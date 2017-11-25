# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render_to_response

class Index(LoginRequiredMixin,View):
    def get(self,request):
        return render_to_response('base_table.html',locals())