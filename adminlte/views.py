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
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib import admin
from django.db import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Div,Field
from crispy_forms.bootstrap import AppendedText,PrependedText
from django_hstore.models import DictionaryField

def get_object_form(app_label,model,excludes=()):  
    ctype = ContentType.objects.get(app_label=app_label,model=model) 
    model_class = ctype.model_class()
  
    class _ObjectForm(forms.ModelForm):
        
        #def __init__(self, *args, **kwargs):
            #Get 'initial' argument if any
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
            #super(_ObjectForm, self).__init__(*args, **kwargs)
    
        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            self.helper.form_class = 'form-horizontal'
            self.helper.label_class = 'col-md-2'
            self.helper.field_class = 'col-md-8'
            #DictionaryField bug
            self.helper.layout = Layout(*[Div(field.name,css_class='form-group') 
                                          for field in model_class._meta.get_fields() 
                                          if not isinstance(field,(models.DateTimeField,models.AutoField,models.ManyToOneRel,DictionaryField,models.ManyToManyRel))])
            super(_ObjectForm, self).__init__(*args, **kwargs)        
        
        class Meta:
            model = model_class
            exclude = excludes
            widgets = {
                #'app': forms.Select(choices=[(data['app_label'],data['app_label']) for data in ContentType.objects.values('app_label').distinct()]),
                #'model':forms.Select(choices=[(data.model,data.model) for data in ContentType.objects.all()]),
                }
            
    return _ObjectForm

class Index(LoginRequiredMixin,View):
    def get(self,request):
        return render_to_response('base_table.html',locals())

class DynamicFormCreate(LoginRequiredMixin,CreateView):
    template_name = 'base_form.html'
        
    def dispatch(self, request, *args, **kwargs):
        app_label = self.kwargs.pop('app_label')
        model = self.kwargs.pop('model')
        self.app_label = app_label
        self.model_name = model
        
        #Handle 404 error!
        try:
            self.form_class = get_object_form(app_label,model,excludes=())
        except ObjectDoesNotExist:
            raise Http404('Objects not found!')
        
        self.success_url = reverse_lazy('dynamic-form-create',args=(app_label,model))
        
        return super(DynamicFormCreate, self).dispatch(request, *args, **kwargs)
    
    def get_form(self, form_class=None):
        form = super(DynamicFormCreate, self).get_form(form_class)
        rel_model = form.Meta.model
        #Automaticlly handle ForeignKey
        for field in rel_model._meta.get_fields():
            if isinstance(rel_model._meta.get_field(field.name), models.ForeignKey):
                rel = field.rel
                form.fields[field.name].widget = RelatedFieldWidgetWrapper(form.fields[field.name].widget, rel,
                                                                          admin.site, can_add_related=True, can_change_related=True)
        return form    
    
    def get_context_data(self, **kwargs):
        context = super(DynamicFormCreate, self).get_context_data(**kwargs)
        context['title'] = 'Add {0} {1}'.format(self.app_label,self.model_name)
        context['app_label'] = self.app_label
        context['model'] = self.model_name
        context['menus'] = {'cmdb':ContentType.objects.filter(app_label='cmdb'),'permission':ContentType.objects.filter(app_label='permission')}
        return context

class DynamicFormUpdate(LoginRequiredMixin,UpdateView):
    template_name = 'base_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        app_label = self.kwargs.pop('app_label')
        model = self.kwargs.pop('model')
        self.app_label = app_label
        self.model_name = model
        
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
        
        self.success_url = reverse_lazy('dynamic-form-create',args=(app_label,model))
        
        return super(DynamicFormUpdate, self).dispatch(request, *args, **kwargs)
    
    def get_form(self, form_class=None):
        form = super(DynamicFormUpdate, self).get_form(form_class)
        rel_model = form.Meta.model
        #Automaticlly handle ForeignKey
        for field in rel_model._meta.get_fields():
            if isinstance(rel_model._meta.get_field(field.name), models.ForeignKey):
                rel = field.rel
                form.fields[field.name].widget = RelatedFieldWidgetWrapper(form.fields[field.name].widget, rel,
                                                                          admin.site, can_add_related=True, can_change_related=True)
        return form    
    
    def get_context_data(self, **kwargs):
        context = super(DynamicFormUpdate, self).get_context_data(**kwargs)
        context['title'] = 'Change {0} {1}'.format(self.app_label,self.model_name)
        context['app_label'] = self.app_label
        context['model'] = self.model_name
        context['menus'] = {'cmdb':ContentType.objects.filter(app_label='cmdb'),'permission':ContentType.objects.filter(app_label='permission')}
        return context    

class DynamicModelList(LoginRequiredMixin,ListView):
    template_name = 'base_table.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.form_class = self.kwargs.pop('model')
        return super(DynamicModelList, self).dispatch(request, *args, **kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        app_label = self.kwargs.get('app_label')
        model = self.kwargs.get('model')
        #Handle 404 error!
        try:
            ctype = ContentType.objects.get(app_label=app_label,model=model) 
            self.model = ctype.model_class()
        except ObjectDoesNotExist:
            raise Http404('Objects not found!')
        
        return super(DynamicModelList, self).dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return self.model.objects.all()