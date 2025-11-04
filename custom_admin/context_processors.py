from django.contrib.auth.models import User
from accounts.models import BanAppeal, UserProfile
from games.models import Game, GameRound
from transactions.models import Transaction, DepositRequest, WithdrawalRequest
from cms.models import Page


def admin_context(request):
    """
    Add admin-related context variables to all templates
    """
    context = {}
    
    # Only add counts if user is staff/admin
    if request.user.is_authenticated and request.user.is_staff:
        # Count total users
        total_users = User.objects.filter(is_staff=False, is_superuser=False).count()
        context['total_users_count'] = total_users
        
        # Count pending deposit requests
        pending_deposits = DepositRequest.objects.filter(status='pending').count()
        context['pending_deposits_count'] = pending_deposits
        
        # Count pending withdrawal requests
        pending_withdrawals = WithdrawalRequest.objects.filter(status='pending').count()
        context['pending_withdrawals_count'] = pending_withdrawals
        
        # Count pending KYC verifications
        pending_kyc = UserProfile.objects.filter(kyc_status='pending').count()
        context['pending_kyc_count'] = pending_kyc
        
        # Count active games
        active_games = Game.objects.filter(status='active').count()
        context['active_games_count'] = active_games
        
        # Count pending ban appeals
        pending_appeals = BanAppeal.objects.filter(status='pending').count()
        context['pending_appeals_count'] = pending_appeals
        
        # Count recent transactions (last 24 hours)
        from django.utils import timezone
        from datetime import timedelta
        recent_time = timezone.now() - timedelta(hours=24)
        recent_transactions = Transaction.objects.filter(created_at__gte=recent_time).count()
        context['recent_transactions_count'] = recent_transactions
        
        # Count total CMS pages
        total_pages = Page.objects.count()
        context['total_cms_pages_count'] = total_pages
    
    return context
