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
from datatableview.views import DatatableView
from datatableview import Datatable, columns
from fm.views import  AjaxDeleteView

def get_object_form(app_label,model,excludes=()):  
    ctype = ContentType.objects.get(app_label=app_label,model=model) 
    model_class = ctype.model_class()
    if not model_class:
        raise Http404("You should register app in the project settings!")
    
    class _ObjectForm(forms.ModelForm):
    
        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            self.helper.form_class = 'form-horizontal'
            self.helper.label_class = 'col-md-2'
            self.helper.field_class = 'col-md-8'
            #DictionaryField bug
            self.helper.layout = Layout(*[Div(field.name,css_class='form-group') 
                                          for field in model_class._meta.get_fields() 
                                          if not isinstance(field,(models.AutoField,models.ManyToOneRel,DictionaryField,models.ManyToManyRel))])
            super(_ObjectForm, self).__init__(*args, **kwargs)        
        
        class Meta:
            model = model_class
            exclude = excludes
            
    return _ObjectForm

class Index(LoginRequiredMixin,View):
    def get(self,request):
        title = 'Index'
        app_label = None
        model = None
        model_name = None
        menus = {'cmdb':ContentType.objects.filter(app_label='cmdb'),'permission':ContentType.objects.filter(app_label='permission')}        
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
        
        self.success_url = reverse_lazy('dynamic-list',args=(app_label,model))
        
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
            elif isinstance(rel_model._meta.get_field(field.name), models.GenericIPAddressField):
                form.fields[field.name].widget = forms.TextInput(attrs={"data-inputmask":"'alias': 'ip'"})
        return form    
    
    def get_context_data(self, **kwargs):
        context = super(DynamicFormCreate, self).get_context_data(**kwargs)
        context['title'] = 'Add {0} {1}'.format(self.app_label,self.model_name)
        context['app_label'] = self.app_label
        context['model'] = self.model_name
        context['model_name'] = self.model_name
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
        
        self.success_url = reverse_lazy('dynamic-list',args=(app_label,model))
        
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
        context['model_name'] = self.model_name
        context['menus'] = {'cmdb':ContentType.objects.filter(app_label='cmdb'),'permission':ContentType.objects.filter(app_label='permission')}
        return context

class DynamicModelList(LoginRequiredMixin,DatatableView):
    template_name = 'base_table.html'
    
    def dispatch(self, request, *args, **kwargs):
        app_label = self.kwargs.pop('app_label')
        model = self.kwargs.pop('model')
        self.app_label = app_label
        self.model_name = model
        
        #Raise 404 error if app_label and model does not exist!
        try:
            ctype = ContentType.objects.get(app_label=app_label,model=model) 
            self.model = ctype.model_class()
        except ObjectDoesNotExist:
            raise Http404('Objects not found!')
        
        if not self.model:
            raise Http404("You should register app in the project settings!")
        
        model = self.model
        
        class datatable_class(Datatable):
            
            #Handle DateTimeField DateField and IP
            def format_date_time(instance, **kwargs):
                return getattr(instance,kwargs['field_name']).strftime('%Y-%m-%d %H:%M:%S')
            
            def format_date(instance, **kwargs):
                return getattr(instance,kwargs['field_name']).strftime('%Y-%m-%d')
            
            def format_ip(instance, **kwargs):
                return getattr(instance,kwargs['field_name'])
    
            self.processors = {}
            self.search_fields = list()
            self.columns = list()

            for field in model._meta.get_fields():
                if isinstance(field,models.DateTimeField):
                    self.processors.update({field.name:format_date_time})
                    self.search_fields.append(field.name)
                    self.columns.append(field.name)
                elif isinstance(field,models.DateField):
                    self.processors.update({field.name:format_date})
                    self.search_fields.append(field.name)
                    self.columns.append(field.name)
                elif isinstance(field,models.GenericIPAddressField):
                    #self.processors.update({field.name:format_ip})
                    #self.columns.append(field.name)
                    pass
                elif isinstance(field,models.CharField):
                    #Handle choice field
                    if len(field.choices) == 0:
                        self.search_fields.append(field.name)
                        self.columns.append(field.name)
                elif isinstance(field,(models.ManyToManyRel,models.ManyToManyField)):
                    pass
                elif isinstance(field,(models.ManyToOneRel,DictionaryField,models.ManyToManyRel)):
                    pass
                elif isinstance(field,models.AutoField):
                    self.search_fields.append(field.name)
                    self.columns.append(field.name)
                elif isinstance(field,models.ForeignKey):
                    self.search_fields.append(field.name)
                    self.columns.append(field.name)                    
                else:
                    self.search_fields.append(field.name)
                    self.columns.append(field.name)

            class Meta:
                model = self.model
                page_length = 10
                columns = self.columns
                processors = self.processors
                search_fields = self.search_fields
                structure_template = 'datatableview/bootstrap_structure.html'
                request_method = 'POST'
                
        self.datatable_class = datatable_class
        return super(DynamicModelList, self).dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(DynamicModelList, self).get_context_data(**kwargs)
        context['title'] = '{0} {1} List'.format(self.app_label,self.model_name)
        context['app_label'] = self.app_label
        context['model'] = self.model_name
        context['model_name'] = self.model_name
        context['menus'] = {'cmdb':ContentType.objects.filter(app_label='cmdb'),'permission':ContentType.objects.filter(app_label='permission')}
        return context
    
    def get_datatable(self):
        datatable = super(DynamicModelList, self).get_datatable()
        for field in self.model._meta.get_fields():
            if isinstance(field,models.GenericIPAddressField):
                datatable.columns[field.name] = columns.TextColumn(field.name, source=field.name)
            elif isinstance(field,models.ManyToManyField):
                
                class ManyToMantFieldColumn(columns.Column):
                    model_field_class = models.ManyToManyField
                    handles_field_classes = [models.ManyToManyField]
                    lookup_types = ()
                
                def ManyToManyFieldProcessor(instance,**kwargs):
                    return '<br>'.join(['<a>{0}</a>'.format(str(data)) for data in kwargs['rich_value'].all()])
                
                datatable.columns[field.name] = ManyToMantFieldColumn(field.name, sources=field.name,processor=ManyToManyFieldProcessor)

        #if datatable.columns.has_key('field_name'):
            #del datatable.columns['field_name']
        def ActionProcessor(instance,**kwargs):
            DetailButton = '<a href="{0}" role="button" class="btn btn-primary">Detail</a>'.format(reverse_lazy('dynamic-form-update',args=(instance._meta.app_label,instance._meta.model_name,instance.pk)))
            DeleteButton = '<a href="{0}" role="button" class="btn btn-danger fm-delete" data-fm-head="Delete this {1}?" data-fm-callback="reload" data-fm-target="#object-{2}">Delete</a>'.format(
                reverse_lazy('dynamic-delete',args=(instance._meta.app_label,instance._meta.model_name,instance.pk)),
                instance._meta.model_name,
                instance.pk)
            UpdateButton = '<a href="{0}" role="button" class="btn btn-success">Update</a>'.format(reverse_lazy('dynamic-form-update',args=(instance._meta.app_label,instance._meta.model_name,instance.pk)))
            return  DetailButton + UpdateButton + DeleteButton
        
        datatable.columns['Action'] = columns.TextColumn('Action',processor=ActionProcessor)
        
        return datatable    

class DynamicDelete(LoginRequiredMixin,AjaxDeleteView):

    model = None
    pk_url_kwarg = 'pk'
    
    def dispatch(self, request, *args, **kwargs):
        app_label = self.kwargs.pop('app_label')
        model = self.kwargs.pop('model')
        self.app_label = app_label
        self.model_name = model
        #Raise 404 error if app_label and model does not exist!
        try:
            ctype = ContentType.objects.get(app_label=app_label,model=model) 
            self.model = ctype.model_class()
        except ObjectDoesNotExist:
            raise Http404('Objects not found!')
        
        if not self.model:
            raise Http404("You should register app in the project settings!")
        
        model = self.model        
        return super(DynamicDelete,self).dispatch(request,*args,**kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(DynamicDelete, self).get_context_data(**kwargs)
        context['title'] = 'Delete {0} {1}'.format(self.app_label,self.model_name)
        context['app_label'] = self.app_label
        context['model'] = self.model_name
        context['model_name'] = self.model_name
        context['menus'] = {'cmdb':ContentType.objects.filter(app_label='cmdb'),'permission':ContentType.objects.filter(app_label='permission')}
        return context