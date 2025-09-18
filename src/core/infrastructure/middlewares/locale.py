"""
Contains all middlewares that are related to locale structure.
"""

from adrf.requests import AsyncRequest, Request
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin


class ForceIgnoreDefaultLanguageMiddleware(MiddlewareMixin):
    """
    Ignore Accept-Language HTTP headers

    This will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via sessions or cookies

    Should be installed *before* any middleware that checks request.META['HTTP_ACCEPT_LANGUAGE'],
    namely django.middleware.locale.LocaleMiddleware
    """

    def process_request(self, request: HttpRequest | AsyncRequest | Request) -> None:
        if "HTTP_ACCEPT_LANGUAGE" in request.META.keys():
            del request.META["HTTP_ACCEPT_LANGUAGE"]
