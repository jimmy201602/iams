from django.conf.urls import url
from adminlte.views import Index

urlpatterns = [
    url(r'^$', Index.as_view(),name='adminlte-index'),
]
