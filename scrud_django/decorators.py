from datetime import timezone
from functools import wraps

from django.utils.cache import get_conditional_response
from django.utils.http import http_date, quote_etag
from rest_framework.response import Response

from scrud_django.utils import get_string_or_evaluate


def scrudful(
    etag_func=None,
    last_modified_func=None,
    schema_link_or_func=None,
    context_link_or_func=None,
    http_schema_or_func=None,
):
    """Decorator to make a view method SCRUDful"""
    # TODO what about 400 Bad Request context and schema?
    def decorator(view_method):
        @wraps(view_method)
        def inner(self, request, *args, **kwargs):
            if request.method in ("PUT", "DELETE"):
                missing_required_headers = []
                if etag_func and not request.META.get("HTTP_IF_MATCH"):
                    missing_required_headers.append("If-Match")
                if last_modified_func and not request.META.get(
                    "HTTP_IF_UNMODIFIED_SINCE"
                ):
                    missing_required_headers.append("If-Unmodified-Since")
                if missing_required_headers:
                    # TODO Define standard error json
                    response = Response(
                        {"missing-required-headers": missing_required_headers},
                        status=400,
                    )
                    return response

            # Compute values (if any) for the requested resource.
            def get_last_modified():
                if last_modified_func:
                    last_modified = last_modified_func(
                        self, request, *args, **kwargs
                    )
                    if last_modified:
                        return http_date(
                            last_modified.replace(
                                tzinfo=timezone.utc
                            ).timestamp()
                        )
                return None

            if request.method not in ("POST", "OPTIONS"):
                etag = (
                    etag_func(self, request, *args, **kwargs)
                    if etag_func
                    else None
                )
                etag = quote_etag(etag) if etag else None
                last_modified = get_last_modified()
            else:
                etag = None
                last_modified = None
            response = get_conditional_response(
                request, etag=etag, last_modified=last_modified
            )
            if response is None:
                response = view_method(self, request, *args, **kwargs)
                schema_link = (
                    get_string_or_evaluate(
                        schema_link_or_func, self, request, *args, **kwargs
                    )
                    or ""
                )
                context_link = (
                    get_string_or_evaluate(
                        context_link_or_func, self, request, *args, **kwargs
                    )
                    or ""
                )
                join_links = ", " if schema_link and context_link else ""
                link_content = schema_link + join_links + context_link
                if etag:
                    response["ETag"] = etag
                if last_modified:
                    response["Last-Modified"] = last_modified
                if link_content:
                    response["Link"] = link_content
            return response

        setattr(inner, "http_schema_or_func", http_schema_or_func)
        return inner

    return decorator


def scrudful_viewset(cls):
    meta = getattr(cls, "Meta", None)
    etag_func = getattr(meta, "etag_func", None)
    last_modified_func = getattr(meta, "last_modified_func", None)
    schema_link_or_func = getattr(meta, "schema_link_or_func", None)
    context_link_or_func = getattr(meta, "context_link_or_func", None)
    scrudful_item = scrudful(
        etag_func=etag_func,
        last_modified_func=last_modified_func,
        schema_link_or_func=schema_link_or_func,
        context_link_or_func=context_link_or_func,
    )
    for method_name in ("create", "retrieve", "update", "destroy"):
        method = getattr(cls, method_name)
        setattr(cls, method_name, scrudful_item(method))
    if hasattr(cls, "list"):
        scrudful_list = scrudful(
            etag_func=getattr(meta, "list_etag_func", None),
            last_modified_func=getattr(meta, "list_last_modified_func", None),
            schema_link_or_func=getattr(
                meta, "list_schema_link_or_func", None
            ),
            context_link_or_func=getattr(
                meta, "list_context_link_or_func", None
            ),
        )
        list_method = getattr(cls, "list")
        setattr(cls, "list", scrudful_list(list_method))
    return cls
