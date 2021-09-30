from rest_framework import status, permissions
from rest_framework.exceptions import APIException

from validators.ErrorCode import ErrorCode
from validators.ErrorMessage import ErrorMessage


class UnauthorizedAccess(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = {"message": ErrorMessage.UNAUTHORIZED_ACCESS, "status": "failed",
                      "code": ErrorCode.UNAUTHORIZED_ACCESS}


class IsAllowedUser(permissions.IsAuthenticated):
    def __init__(self, *user_list):
        self.user_list = user_list

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        else:
            raise UnauthorizedAccess
