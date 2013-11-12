# -*- coding: utf-8 -*-
import pytest

from django.http import HttpResponse, HttpRequest
from django.views.generic import View

from auth_functional import authentication, authorization, or_, and_, not_


def hollow(request, *args, **kwargs):
    assert isinstance(request, HttpRequest)
    return True


def reject(request, *args, **kwargs):
    assert isinstance(request, HttpRequest)
    return False


def true(*args, **kwargs):
    return True


def false(*args, **kwargs):
    return False


@pytest.fixture
def client():
    from django.test.client import Client
    return Client()


@pytest.fixture
def request():
    from django.test.client import RequestFactory
    factory = RequestFactory()
    return factory.get('/some-url')


@pytest.fixture
def view():
    def _view(request, *args, **kwargs):
        return HttpResponse()
    return _view


def test_status_code_is_401_if_authentication_failed(request, view):
    view = authentication(view)
    response = view(request)

    assert response.status_code == 401
    assert "WWW-Authenticate" not in response


def test_status_code_is_403_if_authorization_failed(request, view):
    rejected = authorization(condition=reject)
    view = rejected(view)
    response = view(request)

    assert response.status_code == 403


def test_custom_response_authentication(request, view):
    not_found = lambda *args, **kwargs: HttpResponse(status=404)
    view = authentication(view, response_factory=not_found)
    response = view(request)

    assert response.status_code == 404
    assert "WWW-Authenticate" not in response


def test_custom_response_authorization(request, view):
    not_found = lambda *args, **kwargs: HttpResponse(status=404)
    rejected = authorization(condition=reject, response_factory=not_found)
    view = rejected(view)
    response = view(request)

    assert response.status_code == 404


def test_www_authenticate_is_set_if_provided(request, view):
    header = 'Basic realm="Private"'
    view = authentication(view, www_authenticate=header)
    response = view(request)

    assert response.status_code == 401
    assert response["WWW-Authenticate"] == header


def test_signature_of_decorated_view_authentication(view):
    decorated = authentication(view)

    assert decorated.__name__ == view.__name__
    assert decorated.__doc__ == view.__doc__


def test_signature_of_decorated_view_authorization(view):
    rejected = authorization(condition=reject)
    decorated = rejected(view)

    assert decorated.__name__ == view.__name__
    assert decorated.__doc__ == view.__doc__


def test_signature_of_decorated_view_with_params_authentication(view):
    decorator = authentication(authenticator=lambda *args, **kwargs: True)
    decorated = decorator(view)

    assert decorated.__name__ == view.__name__
    assert decorated.__doc__ == view.__doc__


def test_view_authentication(request):
    @authentication(authenticator=hollow)
    def view(request, *args, **kwargs):
        return HttpResponse()
    response = view(request)

    assert response.status_code == 200


def test_view_authorization(request):
    @authorization(condition=hollow)
    def view(request, *args, **kwargs):
        return HttpResponse()
    response = view(request)

    assert response.status_code == 200


def test_class_based_view_authentication(request):
    class SomeView(View):
        @authentication(authenticator=hollow)
        def get(self, request, *args, **kwargs):
            return HttpResponse()
    view = SomeView.as_view()
    response = view(request)

    assert response.status_code == 200


def test_class_based_view_authorization(request):
    class SomeView(View):
        @authorization(condition=hollow)
        def get(self, request, *args, **kwargs):
            return HttpResponse()
    view = SomeView.as_view()
    response = view(request)

    assert response.status_code == 200


def test_or_decorator():
    assert or_(false, true)()
    assert or_(true, true)()
    assert or_(true, false)()
    assert not or_(false, false)()


def test_and_decorator():
    assert not and_(false, true)()
    assert not and_(true, false)()
    assert not and_(false, false)()
    assert and_(true, true)()


def test_not_decorator():
    assert not_(false)()
    assert not not_(true)()
