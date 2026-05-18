from rest_framework.permissions import BasePermission


class IsOrderOwner(BasePermission):
    """Разрешить доступ только владельцу заказа."""

    def has_object_permission(self, request, view, obj) -> bool:  # noqa: ANN001
        return obj.user_id == request.user.id
