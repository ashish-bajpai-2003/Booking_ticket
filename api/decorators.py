# decorators.py
from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.role != "OWNER":
            return Response({"error": "Admin access only."}, status=status.HTTP_403_FORBIDDEN)
        return view_func(self, request, *args, **kwargs)
    return _wrapped_view

def normal_user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.role != "NORMAL":
            return Response({"error": "Normal user access only."}, status=status.HTTP_403_FORBIDDEN)
        return view_func(self, request, *args, **kwargs)
    return _wrapped_view
