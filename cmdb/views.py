from django.shortcuts import render,HttpResponse
from django.views.generic import TemplateView,View



class Asset(View):
    template_name = "asset.html"
    def get(self,request):
        return render(request,self.template_name)
