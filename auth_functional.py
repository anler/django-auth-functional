# -*- coding: utf-8 -*-
from functools import wraps

from django.http import HttpResponse, HttpRequest
from django.contrib.auth.decorators import login_required as django_login_required


DEFAULT_AUTHENTICATOR = lambda *args, **kwargs: not django_login_required(*args, **kwargs)


class Unauthorized(HttpResponse):
    status_code = 401


def authentication(view=None, authenticator=None, www_authenticate=None, response=None):
    """Check request's authentication.

    :param view: View or class-based view to decorate.
    :param authenticator: Callable that checks request's authentication. If `None` the default
    method: `DEFAULT_AUTHENTICATOR` is used.
    :param www_authenticate: Header to send in the response as a request to the client to
    authenticate if the authentication failed.
    :param response: HTTP response to send if authentication fails. By default a 401 response is
    used.

    :return: HTTP 401 "Unauthorized" response if the authentication failed, otherwise the repsonse
    returned by `view`.
    """
    if authenticator is None:
        authenticator = DEFAULT_AUTHENTICATOR

    def wrapper(view):
        @wraps(view)
        def decorator(*args, **kwargs):
            auth_args = args[1:] if not isinstance(args[0], HttpRequest) else args
            if authenticator(*auth_args, **kwargs):
                return view(*args, **kwargs)
            unauthorized = Unauthorized() if response is None else response
            if www_authenticate is not None:
                unauthorized["WWW-Authenticate"] = www_authenticate
            return unauthorized
        return decorator

    if view is not None:
        wrapper = wrapper(view)
    return wrapper
