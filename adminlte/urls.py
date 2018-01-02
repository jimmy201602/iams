from django.conf.urls import url
from adminlte.views import DynamicFormCreate,DynamicFormUpdate,DynamicModelList,DynamicDelete

urlpatterns = [
    url(r'^form/(?P<app_label>\w+)/(?P<model>\w+)/add/', DynamicFormCreate.as_view(),name='dynamic-form-create'),
    url(r'^form/(?P<app_label>\w+)/(?P<model>\w+)/(?P<pk>[0-9]+)/update/', DynamicFormUpdate.as_view(),name='dynamic-form-update'),
    url(r'^form/(?P<app_label>\w+)/(?P<model>\w+)/list/', DynamicModelList.as_view(),name='dynamic-list'),
    url(r'form/(?P<app_label>\w+)/(?P<model>\w+)/(?P<pk>[0-9]+)/delete/', DynamicDelete.as_view(), name="dynamic-delete"),
]
