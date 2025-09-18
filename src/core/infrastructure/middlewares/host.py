from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin


class MultipleProxyMiddleware(MiddlewareMixin):
    """
    The get_host() method fails when the host is behind multiple proxies.
    One solution is to use middleware to rewrite the proxy headers.

    This middleware should be positioned before any other middleware that
    relies on the value of get_host() - for instance, CommonMiddleware or CsrfViewMiddleware.
    """

    FORWARDED_FOR_FIELDS = [
        "HTTP_X_FORWARDED_FOR",
        "HTTP_X_FORWARDED_HOST",
        "HTTP_X_FORWARDED_SERVER",
    ]

    def process_request(self, request: HttpRequest) -> None:
        """
        Rewrites the proxy headers so that only the most
        recent proxy is used.
        """
        for field in self.FORWARDED_FOR_FIELDS:
            if field in request.META:
                if "," in request.META[field]:
                    parts = request.META[field].split(",")
                    request.META[field] = parts[-1].strip()
