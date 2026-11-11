import logging
from time import perf_counter_ns, strftime

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.cache import add_never_cache_headers
from django.utils.encoding import escape_uri_path


logger = logging.getLogger(__name__)


def _is_api_request(request):
    return request.path_info == "/api" or request.path_info.startswith("/api/")


def log_requests(get_response):
    def middleware(request):
        started_at = perf_counter_ns()
        response = get_response(request)
        duration_ms = (perf_counter_ns() - started_at) // 1_000_000
        headers = []
        values = []
        for header, value in (
            ("time", strftime("%H.%M.%S")),
            ("method", request.method.lower()),
            ("route", escape_uri_path(request.path)),
            ("res.type", str(response.status_code)),
            ("duration", f"{duration_ms}ms"),
        ):
            width = max(len(header), len(value))
            headers.append(header.ljust(width))
            values.append(value.ljust(width))

        log = logger.error if 500 <= response.status_code < 600 else logger.info
        log("%s\n%s", "  ".join(headers).rstrip(), "  ".join(values).rstrip())
        return response

    return middleware


def handle_not_found(get_response):
    def middleware(request):
        response = get_response(request)
        if response.status_code != 404:
            return response

        if _is_api_request(request):
            if request.resolver_match is not None:
                return response
            return JsonResponse(
                {"status": "error", "message": "İstenen API adresi bulunamadı."},
                status=404,
            )

        return render(request, "404.html", status=404)

    return middleware


def guard_server_errors(get_response):
    def middleware(request):
        response = get_response(request)
        if not 500 <= response.status_code < 600:
            return response

        if _is_api_request(request):
            public_error = JsonResponse(
                {"status": "error", "message": "Sunucu isteği şu anda işleyemiyor."}
            )
        else:
            public_error = render(None, "server_error.html", {"status_code": response.status_code})

        if response.streaming:
            response.streaming_content = (public_error.content,)
        else:
            response.content = public_error.content

        response.headers["Content-Type"] = public_error.headers["Content-Type"]
        response.headers["Content-Length"] = str(len(public_error.content))
        response.reason_phrase = None
        for header in ("Content-Encoding", "Content-Disposition", "Content-Range", "ETag", "Last-Modified"):
            response.headers.pop(header, None)
        add_never_cache_headers(response)
        return response

    return middleware
