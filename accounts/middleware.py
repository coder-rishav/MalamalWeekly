from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


class UserPermissionsMiddleware:
    """
    Middleware to enforce user permissions across the platform.
    Checks if users have permission to access specific features.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip permission checks for anonymous users and admin users
        if not request.user.is_authenticated or request.user.is_staff or request.user.is_superuser:
            response = self.get_response(request)
            return response
        
        # Skip checks for these paths
        exempt_paths = [
            '/accounts/login/',
            '/accounts/logout/',
            '/accounts/register/',
            '/admin/',
            '/admin-panel/',
            '/static/',
            '/media/',
        ]
        
        if any(request.path.startswith(path) for path in exempt_paths):
            response = self.get_response(request)
            return response
        
        # Get user profile
        try:
            profile = request.user.profile
        except:
            response = self.get_response(request)
            return response
        
        # Check if user is blocked
        if profile.is_blocked:
            messages.error(request, f'Your account has been banned. Reason: {profile.blocked_reason}')
            return redirect('games:home')
        
        # Define path-to-permission mapping
        permission_checks = {
            '/games/': ('can_view_games', 'You do not have permission to view games.'),
            '/play/': ('can_play_games', 'You do not have permission to play games.'),
            '/transactions/deposit/': ('can_deposit', 'You do not have permission to make deposits.'),
            '/transactions/withdraw/': ('can_withdraw', 'You do not have permission to withdraw funds.'),
            '/transactions/history/': ('can_view_transaction_history', 'You do not have permission to view transaction history.'),
            '/accounts/profile/edit/': ('can_edit_profile', 'You do not have permission to edit your profile.'),
        }
        
        # Check permissions for current path
        for path_prefix, (permission, error_message) in permission_checks.items():
            if request.path.startswith(path_prefix):
                if not getattr(profile, permission, True):
                    messages.error(request, error_message)
                    return redirect('games:dashboard')
        
        response = self.get_response(request)
        return response
