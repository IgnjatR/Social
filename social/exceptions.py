from rest_framework.exceptions import APIException


class EmailDoNotExists(APIException):
    status_code = 400
    default_detail = 'Your email do not exists'
    default_code = 'service_unavailable'


class PostTitleAlreadyExists(APIException):
    status_code = 400
    default_detail = 'Post with that title already exists'
    default_code = 'service_unavailable'
