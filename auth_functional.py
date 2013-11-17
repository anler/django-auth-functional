# -*- coding: utf-8 -*-
from functools import wraps

from django.http import HttpResponse, HttpRequest
from django.contrib.auth.decorators import login_required as django_login_required


def DEFAULT_AUTHENTICATOR(*args, **kwargs):
    return not django_login_required(*args, **kwargs)


class Unauthorized(HttpResponse):
    status_code = 401


def unauthorized_response(*args, **kwargs):
    return Unauthorized()


class Forbidden(HttpResponse):
    status_code = 403


def forbidden_response(*args, **kwargs):
    return Forbidden()


def cleaned_args(args):
    if args and not isinstance(args[0], HttpRequest):
        return args[1:]
    return args


def authentication(view=None, authenticator=None, www_authenticate=None, response_factory=None):
    """Check request's authentication.

    :param view: View or class-based view to decorate.
    :param authenticator: Callable that checks request's authentication. If `None` the default
    method: `DEFAULT_AUTHENTICATOR` is used. The callable is passed the request along with
    args/kwargs passed by the dispatcher.
    :param www_authenticate: Header to send in the response as a request to the client to
    authenticate if the authentication failed.
    :param response_factory: Callable to use for building the response. Useful if you want to
    prepare the response yourself. The callable is passed the request along with args/kwargs
    passed by the dispatcher.

    :return: HTTP 401 "Unauthorized" response if the authentication failed, otherwise the response
    returned by the decorated view.
    """
    if authenticator is None:
        authenticator = DEFAULT_AUTHENTICATOR
    if response_factory is None:
        response_factory = unauthorized_response

    def wrapper(view):
        @wraps(view)
        def decorator(*args, **kwargs):
            if authenticator(*cleaned_args(args), **kwargs):
                return view(*args, **kwargs)
            response = response_factory(*args, **kwargs)
            if www_authenticate is not None:
                response["WWW-Authenticate"] = www_authenticate
            return response
        return decorator

    if view is not None:
        wrapper = wrapper(view)
    return wrapper


def authorization(condition, response_factory=None):
    """Check request's authorization.

    :param condition: Callable that returns `True` if the request is authorized and `False`
    otherwise. The callable is passed the request along with args/kwargs passed by the dispatcher.
    :param response_factory: Callable to use for building the response. Useful if you want to
    prepare the response yourself. The callable is passed the request along with args/kwargs passed
    by the dispatcher.

    :return: HTTP 403 "Forbidden" response if the authorization failed, otherwise the response
    returned by the decorated view.
    """
    if response_factory is None:
        response_factory = forbidden_response

    def wrapper(view):
        @wraps(view)
        def decorator(*args, **kwargs):
            if condition(*cleaned_args(args), **kwargs):
                return view(*args, **kwargs)
            return response_factory(*args, **kwargs)
        return decorator
    return wrapper


def or_(*conditions):
    """Decorator that takes multiple condition functions and returns `True` if one is `True`.

    :param conditions: Multiple condition functions.
    """
    def decorator(*args, **kwargs):
        args = cleaned_args(args)
        return any(condition(*args, **kwargs) for condition in conditions)
    return decorator


def and_(*conditions):
    """Decorator that takes multiple condition functions and the if one is `False` returns `False`.

    :param conditions: Multiple condition functions.
    """
    def decorator(*args, **kwargs):
        args = cleaned_args(args)
        return all(condition(*args, **kwargs) for condition in conditions)
    return decorator


def not_(condition):
    """Decorator that takes a condition and negates its return value.

    :param conditions: Condition function.
    """
    def decorator(*args, **kwargs):
        args = cleaned_args(args)
        return not condition(*args, **kwargs)
    return decorator


class RequestCacheMiddleware(object):
    """Middleware that set a dict-based cache to the request only available during its lifecycle.
    """
    def process_request(self, request):
        type(request).cache = DictCacheDescriptor()


class DictCacheDescriptor(object):
    def __init__(self, cache=None):
        if cache is None:
            cache = {}
        self.cache = cache

    def __get__(self, obj, type=None):
        return self.cache
