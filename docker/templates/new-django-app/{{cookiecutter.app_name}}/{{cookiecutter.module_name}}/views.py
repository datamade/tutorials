from django.shortcuts import render
from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = '{{cookiecutter.module_name}}/index.html'


def page_not_found(request, exception, template_name='{{cookiecutter.module_name}}/404.html'):
    return render(request, template_name, status=404)


def server_error(request, template_name='{{cookiecutter.module_name}}/500.html'):
    return render(request, template_name, status=500)
