from .models import AccessLog


class AccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = request.user if hasattr(request, "user") and request.user.is_authenticated else None
        ip_address = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
        AccessLog.objects.create(
            user=user,
            endpoint=request.path,
            method=request.method,
            status_code=response.status_code,
            ip_address=str(ip_address)[:64],
        )
        return response
