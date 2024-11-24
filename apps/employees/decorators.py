import functools
from rest_framework.views import Response
from rest_framework import status


def instance_check(*check_params, kls):
    def decor_func(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            _instance_params = {param: request.data.get(param) for param in check_params}
            _check = kls.objects.filter(**_instance_params).exists()
            if _check:
                return Response({"success": False, "error": f"{kls.__name__} instance already exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            return func(self, request, *args, **kwargs)
        return wrapper
    return decor_func


class InstanceCheck:
    pass

