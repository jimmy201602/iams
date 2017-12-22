# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render_to_response
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy

def get_object_form(app_label,model,excludes=()):  
    ctype = ContentType.objects.get(app_label=app_label,model=model) 
    model_class = ctype.model_class()
    
    class _ObjectForm( forms.ModelForm ):
        
        #def __init__(self, *args, **kwargs):
            ## Get 'initial' argument if any
            #initial_arguments = kwargs.get('initial', None)
            #updated_initial = {}
            #if initial_arguments:
                ## We have initial arguments, fetch 'user' placeholder variable if any
                #user = initial_arguments.get('user',None)
                ## Now update the form's initial values if user
                #if user:
                    #updated_initial['name'] = getattr(user, 'first_name', None)
                    #updated_initial['email'] = getattr(user, 'email', None)
            ## You can also initialize form fields with hardcoded values
            ## or perform complex DB logic here to then perform initialization
            #updated_initial['comment'] = 'Please provide a comment'
            ## Finally update the kwargs initial reference
            #kwargs.update(initial=updated_initial)
            #super(ContactForm, self).__init__(*args, **kwargs)
        
        class Meta:
            model = model_class
            exclude = excludes
            
    return _ObjectForm

class Index(LoginRequiredMixin,View):
    def get(self,request):
        return render_to_response('base_table.html',locals())

class DynamicFormCreate(LoginRequiredMixin,CreateView):
    template_name = 'base_form.html'
        
    def dispatch(self, request, *args, **kwargs):
        app_label = self.kwargs.pop('app_label')
        model = self.kwargs.pop('model')
        #Handle 404 error!
        try:
            self.form_class = get_object_form(app_label,model,excludes=())
        except ObjectDoesNotExist:
            raise Http404('Objects not found!')
        
        self.success_url = reverse_lazy('dynamic-form-create',args=(app_label,model))
        
        return super(DynamicFormCreate, self).dispatch(request, *args, **kwargs)


class DynamicFormUpdate(LoginRequiredMixin,UpdateView):
    template_name = 'base_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        app_label = self.kwargs.pop('app_label')
        model = self.kwargs.pop('model')
        #Handle 404 error!
        try:
            ctype = ContentType.objects.get(app_label=app_label,model=model) 
            self.model = ctype.model_class()
        except ObjectDoesNotExist:
            raise Http404('Objects not found!')
        #Handle model form error!
        try:
            self.form_class = get_object_form(app_label,model,excludes=())
        except ObjectDoesNotExist:
            raise Http404('Objects not found!')        
        self.queryset = self.model.objects.filter(pk=self.kwargs.get('pk',None))
        
        self.success_url = '/adminlte/form/permission/role/add/'
        
        return super(DynamicFormUpdate, self).dispatch(request, *args, **kwargs)

class DynamicFormList(LoginRequiredMixin,ListView):
    template_name = 'base_table.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.form_class = self.kwargs.pop('model')
        return super(DynamicFormList, self).dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return self.model.objects.all()