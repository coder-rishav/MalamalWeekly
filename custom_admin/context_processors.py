from accounts.models import BanAppeal


def admin_context(request):
    """
    Add admin-related context variables to all templates
    """
    context = {}
    
    # Only add counts if user is staff/admin
    if request.user.is_authenticated and request.user.is_staff:
        # Count pending ban appeals
        pending_appeals = BanAppeal.objects.filter(status='pending').count()
        context['pending_appeals_count'] = pending_appeals
        
        # You can add other counts here in the future
        # e.g., pending_deposits_count, pending_withdrawals_count
    
    return context
