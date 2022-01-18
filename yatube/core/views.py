from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    template = "core/404.html"
    context = {
        'path': request.path
    }
    return render(request, template, context, HTTPStatus.FOUND)


def csrf_failure(request, reason=''):
    template = "core/403csrf.html"
    return render(request, template)


def server_error(request):
    template = "core/500.html"
    return render(request, template)
