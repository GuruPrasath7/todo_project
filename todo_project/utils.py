import datetime

from oauth2_provider.models import RefreshToken, Application, AccessToken
from oauthlib.oauth2.rfc6749.tokens import random_token_generator
from requests import request
from rest_framework import status
from rest_framework.response import Response

from validators.ErrorCode import ErrorCode
from validators.ErrorMessage import ErrorMessage


class CommonUtils(object):
    """
        Common Utility methods
    """

    @staticmethod
    def dispatch_success(response, code=status.HTTP_200_OK, **kwargs):
        if isinstance(response, list) or isinstance(response, dict):
            data = {'status': 'success', 'result': response, **kwargs}
        else:
            message = getattr(ErrorMessage, response)
            data = {'status': 'success', 'message': message, **kwargs}
        return Response(data=data, status=code)

    @staticmethod
    def dispatch_failure(identifier, response=None, code=status.HTTP_400_BAD_REQUEST):
        if hasattr(ErrorCode, identifier):
            error_code = getattr(ErrorCode, identifier)
        else:
            error_code = code
        error_message = getattr(ErrorMessage, identifier)
        errors = {'status': 'failed', 'code': error_code, 'message': error_message}
        if response is not None:
            errors['errors'] = response
        return Response(data=errors, status=code)

    @staticmethod
    def create_access(user):
        """
            Creating oAuth access token for user in login
        """
        expire_seconds = 36000
        scopes = 'read write'

        application = Application.objects.get(name="Authorization")
        expires = datetime.datetime.now() + datetime.timedelta(seconds=expire_seconds)
        access_token = AccessToken.objects.create(
            user=user,
            application=application,
            token=random_token_generator(request),
            expires=expires,
            scope=scopes)

        refresh_token = RefreshToken.objects.create(
            user=user,
            token=random_token_generator(request),
            access_token=access_token,
            application=application)

        token = {
            'access_token': access_token.token,
            'token_type': 'Bearer',
            'expires_in': expire_seconds,
            'refresh_token': refresh_token.token,
            'scope': scopes}
        return token


class DateTimeUtils(object):

    @staticmethod
    def convert_date_string_to_date(date_string, date_format='%d-%m-%Y'):
        return datetime.datetime.strptime(date_string, date_format)

    @staticmethod
    def get_related_datetime(dt, days=0, minutes=0, hours=0, seconds=0):
        return dt + datetime.timedelta(days=days, minutes=minutes, hours=hours, seconds=seconds)

    @staticmethod
    def get_date_difference(date_1, date_2):
        date_1 = date_1.replace(tzinfo=None)
        date_2 = date_2.replace(tzinfo=None)
        if date_1 < date_2:
            return True
        return False
