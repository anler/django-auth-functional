# -*- coding: utf-8 -*-
import pytest

from django.http import HttpResponse

from auth_functional import authentication


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
        from django.http import HttpResponse
        return HttpResponse()
    return _view


def test_status_code_is_401_if_authentication_failed(request, view):
    view = authentication(view)
    response = view(request)

    assert response.status_code == 401
    assert "WWW-Authenticate" not in response


def test_custom_response(request, view):
    not_found = HttpResponse(status=404)
    view = authentication(view, response=not_found)
    response = view(request)

    assert response.status_code == 404
    assert "WWW-Authenticate" not in response


def test_www_authenticate_is_set_if_provided(request, view):
    header = 'Basic realm="Private"'
    view = authentication(view, www_authenticate=header)
    response = view(request)

    assert response.status_code == 401
    assert response["WWW-Authenticate"] == header


def test_signature_of_decorated_view(view):
    decorated = authentication(view)

    assert decorated.__name__ == view.__name__
    assert decorated.__doc__ == view.__doc__


def test_signature_of_decorated_view_with_params(view):
    decorator = authentication(authenticator=lambda *args, **kwargs: True)
    decorated = decorator(view)

    assert decorated.__name__ == view.__name__
    assert decorated.__doc__ == view.__doc__
