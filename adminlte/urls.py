from django.conf.urls import url
from adminlte.views import Index,DynamicFormCreate,DynamicFormUpdate

urlpatterns = [
    url(r'^$', Index.as_view(),name='adminlte-index'),
    url(r'^(?P<app_label>\w+)/(?P<model>\w+)/add/$', DynamicFormCreate.as_view(),name='dynamic-form-create'),
    url(r'^(?P<app_label>\w+)/(?P<model>\w+)/(?P<pk>[0-9]+)/update/$', DynamicFormUpdate.as_view(),name='dynamic-form-update'),
]
