from accounts.models import BanAppeal, UserProfile


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
        
        # Count pending KYC verifications
        pending_kyc = UserProfile.objects.filter(kyc_status='pending').count()
        context['pending_kyc_count'] = pending_kyc
        
        # You can add other counts here in the future
        # e.g., pending_deposits_count, pending_withdrawals_count
    
    return context
