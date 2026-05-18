from __future__ import annotations

from http import HTTPStatus
from typing import Any

from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

DEFAULT_ERROR_DETAIL = "Ошибка обработки запроса."


def error_response(
    *,
    code: str,
    detail: str,
    status_code: int,
    fields: dict[str, Any] | None = None,
) -> Response:
    """Вернуть ошибку API в едином формате ADR 0029."""

    return Response(
        {
            "code": code,
            "detail": detail,
            "fields": fields,
        },
        status=status_code,
    )


def validation_error_response(fields: dict[str, Any]) -> Response:
    """Вернуть ошибку валидации serializer с детализацией по полям."""

    return error_response(
        code="validation_error",
        detail="Ошибка валидации данных.",
        fields=fields,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


def api_exception_handler(exc, context):  # noqa: ANN001
    """Преобразовать стандартные DRF-ошибки в единый JSON-контракт проекта."""

    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        return validation_error_response(_normalize_error_detail(exc.detail))

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return error_response(
            code="authentication_required",
            detail="Необходимо выполнить аутентификацию.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, PermissionDenied):
        return error_response(
            code="permission_denied",
            detail="Недостаточно прав для выполнения операции.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, Http404) or (response is not None and response.status_code == status.HTTP_404_NOT_FOUND):
        return error_response(
            code="not_found",
            detail="Объект не найден.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if response is not None:
        return error_response(
            code=_code_from_status(response.status_code),
            detail=_detail_from_response(response.data, response.status_code),
            status_code=response.status_code,
        )

    return None


def _normalize_error_detail(detail: Any) -> dict[str, Any]:
    if isinstance(detail, dict):
        return {str(key): _normalize_error_list(value) for key, value in detail.items()}

    return {"non_field_errors": _normalize_error_list(detail)}


def _normalize_error_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]

    return [str(value)]


def _code_from_status(status_code: int) -> str:
    if status_code == status.HTTP_404_NOT_FOUND:
        return "not_found"
    if status_code == status.HTTP_403_FORBIDDEN:
        return "permission_denied"
    if status_code == status.HTTP_401_UNAUTHORIZED:
        return "authentication_required"
    if status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        return "server_error"
    return "request_error"


def _detail_from_response(data: Any, status_code: int) -> str:
    if isinstance(data, dict) and data.get("detail"):
        return str(data["detail"])

    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return DEFAULT_ERROR_DETAIL
