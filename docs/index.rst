.. Django Auth Functional documentation master file, created by
   sphinx-quickstart on Thu Nov  7 18:24:38 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Django Auth Functional's documentation!
==================================================

What is this?
-------------

This library provides a set of decorators for working with authentication and authorization. These decorators can be used to decorate plain functions or method in class-based views and you can decide what http response you want to return in the cases where the authentication/authorization failed.

Authenticating your views
-------------------------

In order to authenticate your views all you need to do is decorate your view function:

.. code-block :: python

    from auth_functional import authentication
    from django.template.response import TemplateResponse

    @authentication
    def profile(request):
        return TemplateResponse(request, 'user/profile.html')

Or, in case you're using aa class-base view:

.. code-block :: python

    from auth_functional import authentication
    from django.template.response import TemplateResponse
    from django.views.generic import View

    class SomeView(View):
        @authentication
        def get(self, request):
            return TemplateREsponse(request, 'user/profile.html')


With that in place, all the non-authenticated requests are gonna receive an **HTTP 401 Unauthorized** response.

Returning a different response
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to return a response different than the default **HTTP 401 Unauthorized** you can provide ``response_factory`` callable to the authentication decorator. If the authentication fails your ``response_factory`` callable will be called with **the same parameters as the view**.

.. code-block :: python

    from auth_functional import authentication
    from django.template.response import TemplateResponse
    from django import http


    def unauthorized_response(request):
        response = http.HttpResponse(status=401)
        if 'application/json' in request.META.get('HTTP_ACCEPT'):
            response['Content-Type'] = 'application/json; charset=utf-8'
        return response


    @authentication(response_factory=unauthorized_response)
    def profile(request):
        return TemplateResponse(request, 'user/profile.html')


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
