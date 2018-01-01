from django.conf.urls import url
from adminlte.views import Index,DynamicFormCreate,DynamicFormUpdate,DynamicModelList

urlpatterns = [
    url(r'^$', Index.as_view(),name='adminlte-index'),
    url(r'^form/(?P<app_label>\w+)/(?P<model>\w+)/add/', DynamicFormCreate.as_view(),name='dynamic-form-create'),
    url(r'^form/(?P<app_label>\w+)/(?P<model>\w+)/(?P<pk>[0-9]+)/update/', DynamicFormUpdate.as_view(),name='dynamic-form-update'),
    url(r'^form/(?P<app_label>\w+)/(?P<model>\w+)/list/', DynamicModelList.as_view(),name='dynamic-list'),
]
