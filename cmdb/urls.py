from django.conf.urls import url
from .views import Asset

urlpatterns = [
   # url(r'^$', Index.as_view(),name='adminlte-index'),
   url(r'^$',Asset.as_view()),
]
