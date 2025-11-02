from django.shortcuts import render


def csrf_failure(request, reason=""):
    """
    Custom view for CSRF verification failures.
    This provides a user-friendly error page instead of Django's default.
    """
    return render(request, '403_csrf.html', status=403)


def custom_403(request, exception=None):
    """
    Custom view for 403 Forbidden errors.
    """
    return render(request, '403.html', status=403)


def custom_404(request, exception=None):
    """
    Custom view for 404 Page Not Found errors.
    """
    return render(request, '404.html', status=404)


def custom_500(request):
    """
    Custom view for 500 Internal Server errors.
    """
    return render(request, '500.html', status=500)
