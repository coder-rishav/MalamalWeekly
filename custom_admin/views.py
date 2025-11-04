from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import json
from accounts.models import UserProfile, BanAppeal
from games.models import Game, GameRound, UserEntry, Winner
from transactions.models import Transaction, DepositRequest, WithdrawalRequest, PaymentGateway
from django.contrib.auth.models import User
from cms.models import Page, SocialLink, SiteSettings


def is_admin(user):
    """Check if user is staff or superuser"""
    return user.is_staff or user.is_superuser


def admin_login_view(request):
    """Custom admin login page"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('custom_admin:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and is_admin(user):
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('custom_admin:dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'custom_admin/login.html')


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_logout_view(request):
    """Admin logout"""
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('custom_admin:login')


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_dashboard(request):
    """Main admin dashboard"""
    from datetime import timedelta
    from django.utils import timezone
    from cms.models import Page
    
    # Statistics
    total_users = User.objects.filter(is_staff=False).count()
    total_games = Game.objects.count()
    active_games = Game.objects.filter(status='active').count()
    total_transactions = Transaction.objects.count()
    
    # Financial stats
    total_deposits = Transaction.objects.filter(
        transaction_type='deposit', 
        status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_withdrawals = Transaction.objects.filter(
        transaction_type='withdrawal', 
        status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_game_entries = Transaction.objects.filter(
        transaction_type='game_entry', 
        status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Pending requests
    pending_deposits = DepositRequest.objects.filter(status='pending').count()
    pending_withdrawals = WithdrawalRequest.objects.filter(status='pending').count()
    
    # KYC Statistics
    kyc_pending = UserProfile.objects.filter(kyc_status='pending').count()
    kyc_verified = UserProfile.objects.filter(kyc_status='verified').count()
    kyc_rejected = UserProfile.objects.filter(kyc_status='rejected').count()
    kyc_not_submitted = UserProfile.objects.filter(kyc_status='not_submitted').count()
    
    # Ban Appeals Statistics
    pending_appeals = BanAppeal.objects.filter(status='pending').count()
    approved_appeals = BanAppeal.objects.filter(status='approved').count()
    rejected_appeals = BanAppeal.objects.filter(status='rejected').count()
    
    # Payment Gateway Statistics
    active_gateways = PaymentGateway.objects.filter(is_active=True).count()
    total_gateways = PaymentGateway.objects.count()
    
    # CMS Statistics
    total_pages = Page.objects.count()
    active_pages = Page.objects.filter(is_active=True).count()
    
    # Recent activity
    recent_transactions = Transaction.objects.select_related('user').order_by('-created_at')[:10]
    recent_entries = UserEntry.objects.select_related('user', 'game_round__game').order_by('-created_at')[:10]
    
    # Active rounds
    active_rounds = GameRound.objects.filter(status='open').select_related('game').order_by('-scheduled_end')[:5]
    
    # Recent KYC submissions
    recent_kyc = UserProfile.objects.filter(kyc_status='pending').select_related('user').order_by('-kyc_submitted_at')[:5]
    
    # Chart Data - Last 7 days transactions
    last_7_days = timezone.now() - timedelta(days=7)
    daily_transactions = []
    daily_labels = []
    
    for i in range(6, -1, -1):
        day = timezone.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        deposits = Transaction.objects.filter(
            transaction_type='deposit',
            status='completed',
            created_at__gte=day_start,
            created_at__lt=day_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        withdrawals = Transaction.objects.filter(
            transaction_type='withdrawal',
            status='completed',
            created_at__gte=day_start,
            created_at__lt=day_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        game_entries = Transaction.objects.filter(
            transaction_type='game_entry',
            status='completed',
            created_at__gte=day_start,
            created_at__lt=day_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        daily_transactions.append({
            'date': day.strftime('%b %d'),
            'deposits': float(deposits),
            'withdrawals': float(withdrawals),
            'game_entries': float(game_entries)
        })
        daily_labels.append(day.strftime('%b %d'))
    
    # User growth - Last 30 days
    last_30_days = timezone.now() - timedelta(days=30)
    new_users_count = User.objects.filter(
        is_staff=False,
        date_joined__gte=last_30_days
    ).count()
    
    context = {
        'total_users': total_users,
        'total_games': total_games,
        'active_games': active_games,
        'total_transactions': total_transactions,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_game_entries': total_game_entries,
        'pending_deposits': pending_deposits,
        'pending_withdrawals': pending_withdrawals,
        'recent_transactions': recent_transactions,
        'recent_entries': recent_entries,
        'active_rounds': active_rounds,
        
        # New statistics
        'kyc_pending': kyc_pending,
        'kyc_verified': kyc_verified,
        'kyc_rejected': kyc_rejected,
        'kyc_not_submitted': kyc_not_submitted,
        'pending_appeals': pending_appeals,
        'approved_appeals': approved_appeals,
        'rejected_appeals': rejected_appeals,
        'active_gateways': active_gateways,
        'total_gateways': total_gateways,
        'total_pages': total_pages,
        'active_pages': active_pages,
        'recent_kyc': recent_kyc,
        'new_users_count': new_users_count,
        
        # Chart data
        'daily_transactions': json.dumps(daily_transactions),
        'daily_labels': daily_labels,
    }
    
    return render(request, 'custom_admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def users_list(request):
    """List all users"""
    users = User.objects.filter(is_staff=False).select_related('profile').order_by('-date_joined')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    context = {
        'users': users,
        'search': search,
    }
    return render(request, 'custom_admin/users_list.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def user_detail(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    
    # User's transactions
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:20]
    
    # User's game entries
    entries = UserEntry.objects.filter(user=user).select_related('game_round__game').order_by('-created_at')[:20]
    
    # User's winnings
    winnings = Winner.objects.filter(user=user).select_related('game_round__game').order_by('-announced_at')[:10]
    
    context = {
        'user_obj': user,
        'profile': profile,
        'transactions': transactions,
        'entries': entries,
        'winnings': winnings,
    }
    return render(request, 'custom_admin/user_detail.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def manage_user_permissions(request, user_id):
    """Manage user permissions and restrictions"""
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_permissions':
            # Update all permissions
            profile.can_play_games = request.POST.get('can_play_games') == 'on'
            profile.can_deposit = request.POST.get('can_deposit') == 'on'
            profile.can_withdraw = request.POST.get('can_withdraw') == 'on'
            profile.can_view_games = request.POST.get('can_view_games') == 'on'
            profile.can_view_leaderboard = request.POST.get('can_view_leaderboard') == 'on'
            profile.can_view_transaction_history = request.POST.get('can_view_transaction_history') == 'on'
            profile.can_edit_profile = request.POST.get('can_edit_profile') == 'on'
            
            profile.restriction_notes = request.POST.get('restriction_notes', '')
            profile.last_permission_change = timezone.now()
            profile.permission_changed_by = request.user
            profile.save()
            
            messages.success(request, f'Permissions updated successfully for {user.username}!')
            return redirect('custom_admin:manage_user_permissions', user_id=user_id)
        
        elif action == 'ban_user':
            profile.is_blocked = True
            profile.blocked_reason = request.POST.get('blocked_reason', 'Banned by admin')
            profile.blocked_at = timezone.now()
            profile.blocked_by = request.user
            
            # Disable all permissions when banned
            profile.can_play_games = False
            profile.can_deposit = False
            profile.can_withdraw = False
            profile.can_view_games = False
            
            profile.last_permission_change = timezone.now()
            profile.permission_changed_by = request.user
            profile.save()
            
            messages.success(request, f'User {user.username} has been banned!')
            return redirect('custom_admin:manage_user_permissions', user_id=user_id)
        
        elif action == 'unban_user':
            profile.is_blocked = False
            profile.blocked_reason = None
            profile.blocked_at = None
            profile.blocked_by = None
            
            # Restore default permissions
            profile.can_play_games = True
            profile.can_deposit = True
            profile.can_withdraw = True
            profile.can_view_games = True
            profile.can_view_leaderboard = True
            profile.can_view_transaction_history = True
            profile.can_edit_profile = True
            
            profile.last_permission_change = timezone.now()
            profile.permission_changed_by = request.user
            profile.save()
            
            messages.success(request, f'User {user.username} has been unbanned!')
            return redirect('custom_admin:manage_user_permissions', user_id=user_id)
        
        elif action == 'quick_restrict':
            restriction_type = request.POST.get('restriction_type')
            
            if restriction_type == 'no_games':
                profile.can_play_games = False
                profile.restriction_notes = 'Games restricted by admin'
                messages.success(request, f'Game access restricted for {user.username}')
            elif restriction_type == 'no_withdraw':
                profile.can_withdraw = False
                profile.restriction_notes = 'Withdrawals restricted by admin'
                messages.success(request, f'Withdrawal access restricted for {user.username}')
            elif restriction_type == 'no_deposit':
                profile.can_deposit = False
                profile.restriction_notes = 'Deposits restricted by admin'
                messages.success(request, f'Deposit access restricted for {user.username}')
            elif restriction_type == 'view_only':
                profile.can_play_games = False
                profile.can_deposit = False
                profile.can_withdraw = False
                profile.can_edit_profile = False
                profile.restriction_notes = 'View-only mode'
                messages.success(request, f'{user.username} set to view-only mode')
            
            profile.last_permission_change = timezone.now()
            profile.permission_changed_by = request.user
            profile.save()
            
            return redirect('custom_admin:manage_user_permissions', user_id=user_id)
    
    # Get permission change history (last 10 changes)
    permission_history = UserProfile.objects.filter(
        user=user
    ).values('last_permission_change', 'permission_changed_by__username', 'restriction_notes').order_by('-last_permission_change')[:10]
    
    context = {
        'user_obj': user,
        'profile': profile,
        'permission_history': permission_history,
    }
    return render(request, 'custom_admin/manage_user_permissions.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def deposit_requests(request):
    """Manage deposit requests"""
    status_filter = request.GET.get('status', 'pending')
    
    if status_filter == 'all':
        requests = DepositRequest.objects.all()
    else:
        requests = DepositRequest.objects.filter(status=status_filter)
    
    requests = requests.select_related('user', 'processed_by').order_by('-requested_at')
    
    context = {
        'requests': requests,
        'status_filter': status_filter,
    }
    return render(request, 'custom_admin/deposit_requests.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def approve_deposit(request, request_id):
    """Approve a deposit request"""
    deposit_request = get_object_or_404(DepositRequest, id=request_id)
    
    if deposit_request.status != 'pending':
        messages.error(request, 'This request has already been processed.')
        return redirect('custom_admin:deposit_requests')
    
    user = deposit_request.user
    
    # Create transaction
    transaction = Transaction.objects.create(
        user=user,
        transaction_type='deposit',
        amount=deposit_request.amount,
        payment_method=deposit_request.payment_method,
        status='completed',
        balance_before=user.profile.wallet_balance,
        balance_after=user.profile.wallet_balance + deposit_request.amount,
        description=f'Deposit approved by {request.user.username}',
        completed_at=timezone.now()
    )
    
    # Add credits to user wallet
    user.profile.add_credits(deposit_request.amount)
    
    # Update deposit request
    deposit_request.status = 'approved'
    deposit_request.processed_by = request.user
    deposit_request.processed_at = timezone.now()
    deposit_request.transaction = transaction
    deposit_request.save()
    
    messages.success(request, f'Deposit of ₹{deposit_request.amount} approved for {user.username}')
    return redirect('custom_admin:deposit_requests')


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def reject_deposit(request, request_id):
    """Reject a deposit request"""
    deposit_request = get_object_or_404(DepositRequest, id=request_id)
    
    if deposit_request.status != 'pending':
        messages.error(request, 'This request has already been processed.')
        return redirect('custom_admin:deposit_requests')
    
    if request.method == 'POST':
        admin_notes = request.POST.get('admin_notes', '')
        
        deposit_request.status = 'rejected'
        deposit_request.processed_by = request.user
        deposit_request.processed_at = timezone.now()
        deposit_request.admin_notes = admin_notes
        deposit_request.save()
        
        messages.success(request, f'Deposit request rejected for {deposit_request.user.username}')
        return redirect('custom_admin:deposit_requests')
    
    return render(request, 'custom_admin/reject_deposit.html', {'deposit_request': deposit_request})


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def withdrawal_requests(request):
    """Manage withdrawal requests"""
    status_filter = request.GET.get('status', 'pending')
    
    if status_filter == 'all':
        requests = WithdrawalRequest.objects.all()
    else:
        requests = WithdrawalRequest.objects.filter(status=status_filter)
    
    requests = requests.select_related('user', 'processed_by').order_by('-requested_at')
    
    context = {
        'requests': requests,
        'status_filter': status_filter,
    }
    return render(request, 'custom_admin/withdrawal_requests.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def approve_withdrawal(request, request_id):
    """Approve a withdrawal request"""
    withdrawal_request = get_object_or_404(WithdrawalRequest, id=request_id)
    
    if withdrawal_request.status != 'pending':
        messages.error(request, 'This request has already been processed.')
        return redirect('custom_admin:withdrawal_requests')
    
    user = withdrawal_request.user
    
    # Check if user has sufficient balance
    if user.profile.wallet_balance < withdrawal_request.amount:
        messages.error(request, 'User has insufficient balance.')
        return redirect('custom_admin:withdrawal_requests')
    
    # Create transaction
    transaction = Transaction.objects.create(
        user=user,
        transaction_type='withdrawal',
        amount=withdrawal_request.amount,
        payment_method=withdrawal_request.payment_method,
        status='completed',
        balance_before=user.profile.wallet_balance,
        balance_after=user.profile.wallet_balance - withdrawal_request.amount,
        description=f'Withdrawal approved by {request.user.username}',
        completed_at=timezone.now()
    )
    
    # Deduct credits from user wallet
    user.profile.deduct_credits(withdrawal_request.amount)
    
    # Update withdrawal request
    withdrawal_request.status = 'approved'
    withdrawal_request.processed_by = request.user
    withdrawal_request.processed_at = timezone.now()
    withdrawal_request.transaction = transaction
    withdrawal_request.save()
    
    messages.success(request, f'Withdrawal of ₹{withdrawal_request.amount} approved for {user.username}')
    return redirect('custom_admin:withdrawal_requests')


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def reject_withdrawal(request, request_id):
    """Reject a withdrawal request"""
    withdrawal_request = get_object_or_404(WithdrawalRequest, id=request_id)
    
    if withdrawal_request.status != 'pending':
        messages.error(request, 'This request has already been processed.')
        return redirect('custom_admin:withdrawal_requests')
    
    if request.method == 'POST':
        admin_notes = request.POST.get('admin_notes', '')
        
        withdrawal_request.status = 'rejected'
        withdrawal_request.processed_by = request.user
        withdrawal_request.processed_at = timezone.now()
        withdrawal_request.admin_notes = admin_notes
        withdrawal_request.save()
        
        messages.success(request, f'Withdrawal request rejected for {withdrawal_request.user.username}')
        return redirect('custom_admin:withdrawal_requests')
    
    return render(request, 'custom_admin/reject_withdrawal.html', {'withdrawal_request': withdrawal_request})


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def games_management(request):
    """Manage games"""
    games = Game.objects.all().order_by('-created_at')
    
    context = {
        'games': games,
    }
    return render(request, 'custom_admin/games_management.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def create_game(request):
    """Create a new game"""
    if request.method == 'POST':
        # Create new game
        game = Game()
        game.name = request.POST.get('name')
        game.game_type = request.POST.get('game_type')
        game.description = request.POST.get('description')
        game.rules = request.POST.get('rules')
        game.entry_fee = request.POST.get('entry_fee')
        game.winning_amount = request.POST.get('winning_amount')
        game.min_participants = request.POST.get('min_participants', 2)
        game.max_participants = request.POST.get('max_participants', 1000)
        game.status = request.POST.get('status', 'active')
        game.is_featured = request.POST.get('is_featured') == 'on'
        game.created_by = request.user
        
        # Build game_config based on game type
        game_config = {}
        
        if game.game_type == 'custom':
            # For custom games, build config from form inputs
            input_type = request.POST.get('input_type')
            
            if input_type == 'number':
                game_config = {
                    'input_type': 'number',
                    'number_count': int(request.POST.get('number_count', 1)),
                    'min_value': int(request.POST.get('min_value', 1)),
                    'max_value': int(request.POST.get('max_value', 100)),
                    'allow_duplicates': request.POST.get('allow_duplicates') == 'on',
                }
            elif input_type == 'choice':
                # Parse choices from textarea (one per line)
                choices_text = request.POST.get('choices', '')
                choices = [c.strip() for c in choices_text.split('\n') if c.strip()]
                game_config = {
                    'input_type': 'choice',
                    'choices': choices,
                    'multiple_selection': request.POST.get('multiple_selection') == 'on',
                    'selection_count': int(request.POST.get('selection_count', 1)) if request.POST.get('multiple_selection') == 'on' else 1,
                }
            elif input_type == 'text':
                game_config = {
                    'input_type': 'text',
                    'min_length': int(request.POST.get('min_length', 1)),
                    'max_length': int(request.POST.get('max_length', 100)),
                    'case_sensitive': request.POST.get('case_sensitive') == 'on',
                }
            
            # Winning logic
            game_config['winning_logic'] = request.POST.get('winning_logic', 'exact_match')
            game_config['partial_match_points'] = int(request.POST.get('partial_match_points', 0))
        
        game.game_config = game_config
        
        # Handle image upload
        if 'image' in request.FILES:
            game.image = request.FILES['image']
        
        game.save()
        
        messages.success(request, f'Game "{game.name}" created successfully! You can now create rounds for it.')
        return redirect('custom_admin:game_rounds', game_id=game.id)
    
    context = {}
    return render(request, 'custom_admin/create_game.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def edit_game(request, game_id):
    """Edit game details"""
    game = get_object_or_404(Game, id=game_id)
    
    if request.method == 'POST':
        # Update game details
        game.name = request.POST.get('name')
        game.description = request.POST.get('description')
        game.rules = request.POST.get('rules')
        game.entry_fee = request.POST.get('entry_fee')
        game.winning_amount = request.POST.get('winning_amount')
        game.min_participants = request.POST.get('min_participants')
        game.max_participants = request.POST.get('max_participants')
        game.status = request.POST.get('status')
        game.is_featured = request.POST.get('is_featured') == 'on'
        
        # Handle image upload
        if 'image' in request.FILES:
            game.image = request.FILES['image']
        
        game.save()
        
        messages.success(request, f'{game.name} updated successfully!')
        return redirect('custom_admin:games_management')
    
    context = {
        'game': game,
    }
    return render(request, 'custom_admin/edit_game.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def game_rounds(request, game_id):
    """View game rounds"""
    game = get_object_or_404(Game, id=game_id)
    rounds = game.rounds.all().order_by('-round_number')
    
    context = {
        'game': game,
        'rounds': rounds,
    }
    return render(request, 'custom_admin/game_rounds.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def create_new_round(request, game_id):
    """Create a new round for a game"""
    from datetime import timedelta
    
    game = get_object_or_404(Game, id=game_id)
    
    # Check if there's already an open round
    existing_open = game.rounds.filter(status='open').exists()
    if existing_open:
        messages.warning(request, 'This game already has an open round. Close or complete it first.')
        return redirect('custom_admin:game_rounds', game_id=game_id)
    
    if request.method == 'POST':
        duration_days = int(request.POST.get('duration_days', 7))
        
        # Get the last round number
        last_round = game.rounds.order_by('-round_number').first()
        next_round_number = (last_round.round_number + 1) if last_round else 1
        
        # Create new round
        now = timezone.now()
        game_round = GameRound.objects.create(
            game=game,
            round_number=next_round_number,
            scheduled_start=now,
            scheduled_end=now + timedelta(days=duration_days),
            actual_start=now,
            status='open',
            created_by=request.user
        )
        
        messages.success(request, f'Round #{game_round.round_number} created successfully! Entry open for {duration_days} days.')
        return redirect('custom_admin:game_rounds', game_id=game_id)
    
    # GET request - show form
    context = {
        'game': game,
    }
    return render(request, 'custom_admin/create_round.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def close_round(request, round_id):
    """Close a round for entries"""
    game_round = get_object_or_404(GameRound, id=round_id)
    
    if game_round.status != 'open':
        messages.error(request, 'Only open rounds can be closed.')
        return redirect('custom_admin:game_rounds', game_id=game_round.game.id)
    
    # Close the round
    game_round.status = 'closed'
    game_round.actual_end = timezone.now()
    game_round.save()
    
    messages.success(request, f'Round #{game_round.round_number} has been closed. You can now select a winner.')
    return redirect('custom_admin:game_rounds', game_id=game_round.game.id)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def select_winner(request, round_id):
    """Select winner for a round - Random or Manual"""
    import random
    
    game_round = get_object_or_404(GameRound, id=round_id)
    
    if game_round.status != 'closed':
        messages.error(request, 'Can only select winners for closed rounds.')
        return redirect('custom_admin:game_rounds', game_id=game_round.game.id)
    
    # Get all entries for this round
    entries = UserEntry.objects.filter(game_round=game_round).select_related('user')
    
    if not entries.exists():
        messages.error(request, 'No entries found for this round.')
        return redirect('custom_admin:game_rounds', game_id=game_round.game.id)
    
    # Check if winner already exists
    if Winner.objects.filter(game_round=game_round).exists():
        messages.error(request, 'Winner already selected for this round.')
        return redirect('custom_admin:game_rounds', game_id=game_round.game.id)
    
    if request.method == 'POST':
        selection_method = request.POST.get('selection_method')
        
        if selection_method == 'auto':
            # Automatic winner selection based on game type
            game = game_round.game
            winning_combination = None
            winners = []
            
            if game.game_type == 'number_match':
                # Generate 5 random numbers between 0-99
                winning_combination = [random.randint(0, 99) for _ in range(5)]
                
                # Find entries that match the exact sequence
                for entry in entries:
                    if entry.user_choice == winning_combination:
                        winners.append(entry)
            
            elif game.game_type == 'lucky_draw':
                # Generate 1 random number between 1-100
                winning_combination = [random.randint(1, 100)]
                
                # Find entries that match the number
                for entry in entries:
                    if entry.user_choice == winning_combination:
                        winners.append(entry)
            
            elif game.game_type == 'color_game':
                # Select random color
                colors = ['red', 'green', 'blue', 'yellow']
                winning_combination = [random.choice(colors)]
                
                # Find entries that match the color
                for entry in entries:
                    if entry.user_choice == winning_combination:
                        winners.append(entry)
            
            elif game.game_type == 'custom':
                # Handle custom game types
                config = game.game_config
                winning_logic = config.get('winning_logic', 'exact_match')
                
                if config.get('input_type') == 'number':
                    # Generate random numbers
                    number_count = config.get('number_count', 1)
                    min_val = config.get('min_value', 1)
                    max_val = config.get('max_value', 100)
                    
                    winning_combination = [random.randint(min_val, max_val) for _ in range(number_count)]
                    
                    if winning_logic == 'exact_match':
                        for entry in entries:
                            if entry.user_choice == winning_combination:
                                winners.append(entry)
                    elif winning_logic == 'partial_match':
                        # Score based on partial matches
                        entry_scores = []
                        for entry in entries:
                            score = sum(1 for i, num in enumerate(entry.user_choice) if i < len(winning_combination) and num == winning_combination[i])
                            entry_scores.append((entry, score))
                        # Get highest score
                        if entry_scores:
                            max_score = max(s[1] for s in entry_scores)
                            winners = [e[0] for e in entry_scores if e[1] == max_score and e[1] > 0]
                    elif winning_logic == 'closest':
                        # Find closest to winning number
                        if number_count == 1:
                            entry_distances = []
                            for entry in entries:
                                distance = abs(entry.user_choice[0] - winning_combination[0])
                                entry_distances.append((entry, distance))
                            min_distance = min(d[1] for d in entry_distances)
                            winners = [e[0] for e in entry_distances if e[1] == min_distance]
                    elif winning_logic == 'random':
                        # Pick random winner(s)
                        winners = [random.choice(list(entries))]
                
                elif config.get('input_type') == 'choice':
                    # Pick random choice(s)
                    choices = config.get('choices', [])
                    if config.get('multiple_selection', False):
                        selection_count = config.get('selection_count', 1)
                        winning_combination = random.sample(choices, min(selection_count, len(choices)))
                    else:
                        winning_combination = [random.choice(choices)]
                    
                    if winning_logic == 'exact_match':
                        for entry in entries:
                            if sorted(entry.user_choice) == sorted(winning_combination):
                                winners.append(entry)
                    elif winning_logic == 'random':
                        winners = [random.choice(list(entries))]
                
                elif config.get('input_type') == 'text':
                    # Generate random text or pick from entries
                    if winning_logic == 'random':
                        # Pick random winner
                        winners = [random.choice(list(entries))]
                        winning_combination = winners[0].user_choice
                    else:
                        # For text games, admin should set a winning answer manually
                        # For now, just pick random
                        winners = [random.choice(list(entries))]
                        winning_combination = winners[0].user_choice
            
            # Save winning combination
            game_round.winning_combination = winning_combination
            game_round.save()
            
            if not winners:
                messages.warning(request, f'No matching entries found! Winning combination: {winning_combination}. No winner for this round.')
                game_round.status = 'completed'
                game_round.has_winner = False
                game_round.result_announced_at = timezone.now()
                game_round.save()
                return redirect('custom_admin:game_rounds', game_id=game_round.game.id)
            
            # If multiple winners, split prize or select first one
            if len(winners) > 1:
                # Split prize equally among winners
                prize_per_winner = game_round.game.winning_amount / len(winners)
                winner_names = []
                
                for entry in winners:
                    # Create winner
                    winner = Winner.objects.create(
                        game_round=game_round,
                        user=entry.user,
                        entry=entry,
                        prize_amount=prize_per_winner,
                        announced_at=timezone.now()
                    )
                    
                    # Add prize to user wallet
                    entry.user.profile.add_credits(prize_per_winner)
                    
                    # Create transaction
                    Transaction.objects.create(
                        user=entry.user,
                        transaction_type='prize',
                        amount=prize_per_winner,
                        status='completed',
                        balance_before=entry.user.profile.wallet_balance - prize_per_winner,
                        balance_after=entry.user.profile.wallet_balance,
                        description=f'Prize for {game_round.game.name} - Round {game_round.round_number}',
                        completed_at=timezone.now()
                    )
                    
                    # Mark entry as winner
                    entry.is_winner = True
                    entry.save()
                    
                    winner_names.append(entry.user.username)
                
                game_round.status = 'completed'
                game_round.has_winner = True
                game_round.result_announced_at = timezone.now()
                game_round.save()
                
                messages.success(request, f'{len(winners)} winners found! Winning combination: {winning_combination}. Prize split: ₹{prize_per_winner} each to {", ".join(winner_names)}')
            else:
                # Single winner
                entry = winners[0]
                
                # Create winner
                winner = Winner.objects.create(
                    game_round=game_round,
                    user=entry.user,
                    entry=entry,
                    prize_amount=game_round.game.winning_amount,
                    announced_at=timezone.now()
                )
                
                # Add prize to user wallet
                entry.user.profile.add_credits(winner.prize_amount)
                
                # Create transaction
                Transaction.objects.create(
                    user=entry.user,
                    transaction_type='prize',
                    amount=winner.prize_amount,
                    status='completed',
                    balance_before=entry.user.profile.wallet_balance - winner.prize_amount,
                    balance_after=entry.user.profile.wallet_balance,
                    description=f'Prize for {game_round.game.name} - Round {game_round.round_number}',
                    completed_at=timezone.now()
                )
                
                # Update round status
                game_round.status = 'completed'
                game_round.has_winner = True
                game_round.result_announced_at = timezone.now()
                game_round.save()
                
                # Mark entry as winner
                entry.is_winner = True
                entry.save()
                
                messages.success(request, f'Winner found! {entry.user.username} won ₹{winner.prize_amount}. Winning combination: {winning_combination}')
            
            return redirect('custom_admin:game_rounds', game_id=game_round.game.id)
        
        elif selection_method == 'manual':
            # Manual winner selection (old method)
            entry_id = request.POST.get('entry_id')
            entry = get_object_or_404(UserEntry, id=entry_id, game_round=game_round)
            
            # Create winner
            winner = Winner.objects.create(
                game_round=game_round,
                user=entry.user,
                entry=entry,
                prize_amount=game_round.game.winning_amount,
                announced_at=timezone.now()
            )
            
            # Add prize to user wallet
            entry.user.profile.add_credits(winner.prize_amount)
            
            # Create transaction
            Transaction.objects.create(
                user=entry.user,
                transaction_type='prize',
                amount=winner.prize_amount,
                status='completed',
                balance_before=entry.user.profile.wallet_balance - winner.prize_amount,
                balance_after=entry.user.profile.wallet_balance,
                description=f'Prize for {game_round.game.name} - Round {game_round.round_number}',
                completed_at=timezone.now()
            )
            
            # Update round status
            game_round.status = 'completed'
            game_round.has_winner = True
            game_round.result_announced_at = timezone.now()
            game_round.save()
            
            # Mark entry as winner
            entry.is_winner = True
            entry.save()
            
            messages.success(request, f'Winner manually selected! {entry.user.username} won ₹{winner.prize_amount}')
            return redirect('custom_admin:game_rounds', game_id=game_round.game.id)
    
    context = {
        'game_round': game_round,
        'entries': entries,
    }
    return render(request, 'custom_admin/select_winner.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def transactions_list(request):
    """View all transactions"""
    transaction_type = request.GET.get('type', 'all')
    
    if transaction_type == 'all':
        transactions = Transaction.objects.all()
    else:
        transactions = Transaction.objects.filter(transaction_type=transaction_type)
    
    transactions = transactions.select_related('user').order_by('-created_at')[:100]
    
    context = {
        'transactions': transactions,
        'transaction_type': transaction_type,
    }
    return render(request, 'custom_admin/transactions_list.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def ban_appeals_list(request):
    """View all ban appeals"""
    status_filter = request.GET.get('status', 'pending')
    
    from accounts.models import BanAppeal
    
    if status_filter == 'all':
        appeals = BanAppeal.objects.all()
    else:
        appeals = BanAppeal.objects.filter(status=status_filter)
    
    appeals = appeals.select_related('user', 'reviewed_by').order_by('-submitted_at')
    
    context = {
        'appeals': appeals,
        'status_filter': status_filter,
    }
    return render(request, 'custom_admin/ban_appeals.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def review_appeal(request, appeal_id):
    """Review and respond to a ban appeal"""
    from accounts.models import BanAppeal
    
    appeal = get_object_or_404(BanAppeal, id=appeal_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_response = request.POST.get('admin_response', '')
        
        if action == 'approve':
            # Approve appeal and unban user
            appeal.status = 'approved'
            appeal.reviewed_at = timezone.now()
            appeal.reviewed_by = request.user
            appeal.admin_response = admin_response
            appeal.save()
            
            # Unban the user
            profile = appeal.user.profile
            profile.is_blocked = False
            profile.blocked_reason = None
            profile.blocked_at = None
            profile.blocked_by = None
            
            # Restore default permissions
            profile.can_play_games = True
            profile.can_deposit = True
            profile.can_withdraw = True
            profile.can_view_games = True
            profile.can_view_leaderboard = True
            profile.can_view_transaction_history = True
            profile.can_edit_profile = True
            
            profile.last_permission_change = timezone.now()
            profile.permission_changed_by = request.user
            profile.save()
            
            messages.success(request, f'Appeal approved! User {appeal.user.username} has been unbanned.')
            
        elif action == 'reject':
            # Reject appeal
            appeal.status = 'rejected'
            appeal.reviewed_at = timezone.now()
            appeal.reviewed_by = request.user
            appeal.admin_response = admin_response
            appeal.save()
            
            messages.success(request, f'Appeal rejected for user {appeal.user.username}.')
        
        return redirect('custom_admin:ban_appeals_list')
    
    context = {
        'appeal': appeal,
    }
    return render(request, 'custom_admin/review_appeal.html', context)


# ==================== PAYMENT GATEWAY MANAGEMENT ====================

@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def payment_gateways_list(request):
    """List all configured payment gateways"""
    from transactions.models import PaymentGateway
    
    gateways = PaymentGateway.objects.all().order_by('display_order', 'name')
    
    # Count active gateways
    active_count = gateways.filter(is_active=True).count()
    test_mode_count = gateways.filter(mode='test').count()
    live_mode_count = gateways.filter(mode='live').count()
    
    context = {
        'gateways': gateways,
        'active_count': active_count,
        'test_mode_count': test_mode_count,
        'live_mode_count': live_mode_count,
    }
    return render(request, 'custom_admin/payment_gateways_list.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def add_payment_gateway(request):
    """Add a new payment gateway"""
    from transactions.models import PaymentGateway
    
    if request.method == 'POST':
        try:
            gateway = PaymentGateway.objects.create(
                name=request.POST.get('name'),
                provider=request.POST.get('provider'),
                description=request.POST.get('description', ''),
                is_active=request.POST.get('is_active') == 'on',
                mode=request.POST.get('mode', 'test'),
                display_order=int(request.POST.get('display_order', 0)),
                
                # Test credentials
                test_api_key=request.POST.get('test_api_key', ''),
                test_api_secret=request.POST.get('test_api_secret', ''),
                test_merchant_id=request.POST.get('test_merchant_id', ''),
                test_additional_config=request.POST.get('test_additional_config', ''),
                
                # Live credentials
                live_api_key=request.POST.get('live_api_key', ''),
                live_api_secret=request.POST.get('live_api_secret', ''),
                live_merchant_id=request.POST.get('live_merchant_id', ''),
                live_additional_config=request.POST.get('live_additional_config', ''),
                
                # Webhook
                webhook_secret=request.POST.get('webhook_secret', ''),
                webhook_url=request.POST.get('webhook_url', ''),
                
                # UI
                logo_url=request.POST.get('logo_url', ''),
                button_color=request.POST.get('button_color', '#007bff'),
                
                # Limits
                min_amount=float(request.POST.get('min_amount', 10)),
                max_amount=float(request.POST.get('max_amount', 100000)),
                transaction_fee_percent=float(request.POST.get('transaction_fee_percent', 0)),
                transaction_fee_fixed=float(request.POST.get('transaction_fee_fixed', 0)),
                
                # Metadata
                created_by=request.user,
                updated_by=request.user,
            )
            
            messages.success(request, f'Payment gateway "{gateway.name}" added successfully!')
            return redirect('custom_admin:payment_gateways_list')
            
        except Exception as e:
            messages.error(request, f'Error adding gateway: {str(e)}')
    
    context = {
        'providers': PaymentGateway.PROVIDER_CHOICES,
        'modes': PaymentGateway.MODE_CHOICES,
    }
    return render(request, 'custom_admin/add_payment_gateway.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def edit_payment_gateway(request, gateway_id):
    """Edit existing payment gateway"""
    from transactions.models import PaymentGateway
    
    gateway = get_object_or_404(PaymentGateway, id=gateway_id)
    
    if request.method == 'POST':
        try:
            gateway.name = request.POST.get('name')
            gateway.provider = request.POST.get('provider')
            gateway.description = request.POST.get('description', '')
            gateway.is_active = request.POST.get('is_active') == 'on'
            gateway.mode = request.POST.get('mode', 'test')
            gateway.display_order = int(request.POST.get('display_order', 0))
            
            # Test credentials
            gateway.test_api_key = request.POST.get('test_api_key', '')
            gateway.test_api_secret = request.POST.get('test_api_secret', '')
            gateway.test_merchant_id = request.POST.get('test_merchant_id', '')
            gateway.test_additional_config = request.POST.get('test_additional_config', '')
            
            # Live credentials
            gateway.live_api_key = request.POST.get('live_api_key', '')
            gateway.live_api_secret = request.POST.get('live_api_secret', '')
            gateway.live_merchant_id = request.POST.get('live_merchant_id', '')
            gateway.live_additional_config = request.POST.get('live_additional_config', '')
            
            # Webhook
            gateway.webhook_secret = request.POST.get('webhook_secret', '')
            gateway.webhook_url = request.POST.get('webhook_url', '')
            
            # UI
            gateway.logo_url = request.POST.get('logo_url', '')
            gateway.button_color = request.POST.get('button_color', '#007bff')
            
            # Limits
            gateway.min_amount = float(request.POST.get('min_amount', 10))
            gateway.max_amount = float(request.POST.get('max_amount', 100000))
            gateway.transaction_fee_percent = float(request.POST.get('transaction_fee_percent', 0))
            gateway.transaction_fee_fixed = float(request.POST.get('transaction_fee_fixed', 0))
            
            gateway.updated_by = request.user
            gateway.save()
            
            messages.success(request, f'Payment gateway "{gateway.name}" updated successfully!')
            return redirect('custom_admin:payment_gateways_list')
            
        except Exception as e:
            messages.error(request, f'Error updating gateway: {str(e)}')
    
    context = {
        'gateway': gateway,
        'providers': PaymentGateway.PROVIDER_CHOICES,
        'modes': PaymentGateway.MODE_CHOICES,
    }
    return render(request, 'custom_admin/edit_payment_gateway.html', context)


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def toggle_gateway_status(request, gateway_id):
    """Toggle gateway active status"""
    from transactions.models import PaymentGateway
    
    gateway = get_object_or_404(PaymentGateway, id=gateway_id)
    gateway.is_active = not gateway.is_active
    gateway.updated_by = request.user
    gateway.save()
    
    status = 'activated' if gateway.is_active else 'deactivated'
    messages.success(request, f'Payment gateway "{gateway.name}" has been {status}.')
    return redirect('custom_admin:payment_gateways_list')


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def toggle_gateway_mode(request, gateway_id):
    """Toggle gateway between test and live mode"""
    from transactions.models import PaymentGateway
    
    gateway = get_object_or_404(PaymentGateway, id=gateway_id)
    gateway.mode = 'live' if gateway.mode == 'test' else 'test'
    gateway.updated_by = request.user
    gateway.save()
    
    messages.success(request, f'Payment gateway "{gateway.name}" switched to {gateway.get_mode_display()}.')
    return redirect('custom_admin:payment_gateways_list')


@login_required
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def delete_payment_gateway(request, gateway_id):
    """Delete a payment gateway"""
    from transactions.models import PaymentGateway
    
    gateway = get_object_or_404(PaymentGateway, id=gateway_id)
    
    # Check if gateway has transactions
    if gateway.transactions.exists():
        messages.error(request, f'Cannot delete "{gateway.name}" as it has associated transactions.')
        return redirect('custom_admin:payment_gateways_list')
    
    gateway_name = gateway.name
    gateway.delete()
    messages.success(request, f'Payment gateway "{gateway_name}" deleted successfully.')
    return redirect('custom_admin:payment_gateways_list')


# ===== CMS Management =====

@login_required
@user_passes_test(is_admin)
def cms_pages_list(request):
    """List all CMS pages with search functionality"""
    search_query = request.GET.get('search', '')
    filter_section = request.GET.get('section', '')
    filter_status = request.GET.get('status', '')
    
    pages = Page.objects.all().order_by('footer_section', 'order')
    
    if search_query:
        pages = pages.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    if filter_section:
        pages = pages.filter(footer_section=filter_section)
    
    if filter_status:
        is_active = filter_status == 'active'
        pages = pages.filter(is_active=is_active)
    
    # Calculate statistics
    all_pages = Page.objects.all()
    active_pages = all_pages.filter(is_active=True).count()
    quick_links_count = all_pages.filter(footer_section='quick_links').count()
    information_count = all_pages.filter(footer_section='information').count()
    
    context = {
        'pages': pages,
        'search_query': search_query,
        'filter_section': filter_section,
        'filter_status': filter_status,
        'total_pages': all_pages.count(),
        'active_pages': active_pages,
        'quick_links_count': quick_links_count,
        'information_count': information_count,
    }
    return render(request, 'custom_admin/cms_pages_list.html', context)


@login_required
@user_passes_test(is_admin)
def cms_page_create(request):
    """Create a new CMS page"""
    if request.method == 'POST':
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        content = request.POST.get('content')
        meta_description = request.POST.get('meta_description', '')
        show_in_footer = request.POST.get('show_in_footer') == 'on'
        footer_section = request.POST.get('footer_section', 'information')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            page = Page.objects.create(
                title=title,
                slug=slug,
                content=content,
                meta_description=meta_description,
                show_in_footer=show_in_footer,
                footer_section=footer_section,
                order=int(order),
                is_active=is_active,
                created_by=request.user
            )
            messages.success(request, f'Page "{page.title}" created successfully!')
            return redirect('custom_admin:cms_pages_list')
        except Exception as e:
            messages.error(request, f'Error creating page: {str(e)}')
    
    return render(request, 'custom_admin/cms_page_form.html', {'action': 'Create'})


@login_required
@user_passes_test(is_admin)
def cms_page_edit(request, page_id):
    """Edit an existing CMS page"""
    page = get_object_or_404(Page, id=page_id)
    
    if request.method == 'POST':
        page.title = request.POST.get('title')
        page.slug = request.POST.get('slug')
        page.content = request.POST.get('content')
        page.meta_description = request.POST.get('meta_description', '')
        page.show_in_footer = request.POST.get('show_in_footer') == 'on'
        page.footer_section = request.POST.get('footer_section', 'information')
        page.order = int(request.POST.get('order', 0))
        page.is_active = request.POST.get('is_active') == 'on'
        
        try:
            page.save()
            messages.success(request, f'Page "{page.title}" updated successfully!')
            return redirect('custom_admin:cms_pages_list')
        except Exception as e:
            messages.error(request, f'Error updating page: {str(e)}')
    
    context = {
        'page': page,
        'action': 'Edit'
    }
    return render(request, 'custom_admin/cms_page_form.html', context)


@login_required
@user_passes_test(is_admin)
def cms_page_delete(request, page_id):
    """Delete a CMS page"""
    page = get_object_or_404(Page, id=page_id)
    page_title = page.title
    page.delete()
    messages.success(request, f'Page "{page_title}" deleted successfully!')
    return redirect('custom_admin:cms_pages_list')


@login_required
@user_passes_test(is_admin)
def cms_page_toggle_status(request, page_id):
    """Toggle active status of a CMS page"""
    page = get_object_or_404(Page, id=page_id)
    page.is_active = not page.is_active
    page.save()
    
    status = 'activated' if page.is_active else 'deactivated'
    messages.success(request, f'Page "{page.title}" {status} successfully!')
    return redirect('custom_admin:cms_pages_list')


@login_required
@user_passes_test(is_admin)
def cms_social_links(request):
    """Manage social media links"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            platform = request.POST.get('platform')
            url = request.POST.get('url')
            icon_class = request.POST.get('icon_class')
            order = request.POST.get('order', 0)
            is_active = request.POST.get('is_active') == 'on'
            
            try:
                link = SocialLink.objects.create(
                    platform=platform,
                    url=url,
                    icon_class=icon_class,
                    order=int(order),
                    is_active=is_active
                )
                messages.success(request, f'{link.get_platform_display()} link added successfully!')
            except Exception as e:
                messages.error(request, f'Error creating link: {str(e)}')
        
        elif action == 'edit':
            link_id = request.POST.get('link_id')
            link = get_object_or_404(SocialLink, id=link_id)
            
            link.platform = request.POST.get('platform')
            link.url = request.POST.get('url')
            link.icon_class = request.POST.get('icon_class')
            link.order = int(request.POST.get('order', 0))
            link.is_active = request.POST.get('is_active') == 'on'
            
            try:
                link.save()
                messages.success(request, f'{link.get_platform_display()} link updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating link: {str(e)}')
        
        elif action == 'delete':
            link_id = request.POST.get('link_id')
            link = get_object_or_404(SocialLink, id=link_id)
            platform = link.get_platform_display()
            link.delete()
            messages.success(request, f'{platform} link deleted successfully!')
        
        elif action == 'toggle':
            link_id = request.POST.get('link_id')
            link = get_object_or_404(SocialLink, id=link_id)
            link.is_active = not link.is_active
            link.save()
            status = 'activated' if link.is_active else 'deactivated'
            messages.success(request, f'{link.get_platform_display()} link {status}!')
        
        return redirect('custom_admin:cms_social_links')
    
    social_links = SocialLink.objects.all().order_by('order')
    
    context = {
        'social_links': social_links,
        'platform_choices': SocialLink.PLATFORM_CHOICES,
    }
    return render(request, 'custom_admin/cms_social_links.html', context)


@login_required
@user_passes_test(is_admin)
def cms_site_settings(request):
    """Edit global site settings"""
    settings = SiteSettings.get_settings()
    
    if request.method == 'POST':
        settings.site_name = request.POST.get('site_name')
        settings.tagline = request.POST.get('tagline', '')
        settings.description = request.POST.get('description', '')
        settings.contact_email = request.POST.get('contact_email', '')
        settings.contact_phone = request.POST.get('contact_phone', '')
        settings.contact_address = request.POST.get('contact_address', '')
        settings.support_hours = request.POST.get('support_hours', '')
        settings.footer_copyright = request.POST.get('footer_copyright', '')
        settings.footer_tagline = request.POST.get('footer_tagline', '')
        settings.meta_keywords = request.POST.get('meta_keywords', '')
        settings.google_analytics_id = request.POST.get('google_analytics_id', '')
        
        try:
            settings.save()
            messages.success(request, 'Site settings updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')
        
        return redirect('custom_admin:cms_site_settings')
    
    context = {
        'settings': settings,
    }
    return render(request, 'custom_admin/cms_site_settings.html', context)


# ===== KYC Management =====

@login_required
@user_passes_test(is_admin)
def kyc_requests_list(request):
    """List all KYC requests with filtering"""
    status_filter = request.GET.get('status', 'pending')
    search_query = request.GET.get('search', '')
    
    # Base query
    kyc_requests = UserProfile.objects.select_related('user').exclude(kyc_status='not_submitted')
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        kyc_requests = kyc_requests.filter(kyc_status=status_filter)
    
    # Apply search filter
    if search_query:
        kyc_requests = kyc_requests.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(aadhar_number__icontains=search_query) |
            Q(pan_number__icontains=search_query)
        )
    
    # Order by submission date (newest first)
    kyc_requests = kyc_requests.order_by('-kyc_submitted_at')
    
    # Count statistics
    total_submitted = UserProfile.objects.exclude(kyc_status='not_submitted').count()
    pending_count = UserProfile.objects.filter(kyc_status='pending').count()
    verified_count = UserProfile.objects.filter(kyc_status='verified').count()
    rejected_count = UserProfile.objects.filter(kyc_status='rejected').count()
    
    context = {
        'kyc_requests': kyc_requests,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_submitted': total_submitted,
        'pending_count': pending_count,
        'verified_count': verified_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'custom_admin/kyc_requests_list.html', context)


@login_required
@user_passes_test(is_admin)
def kyc_review(request, user_id):
    """Review KYC documents for a specific user"""
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    
    context = {
        'kyc_user': user,
        'profile': profile,
    }
    return render(request, 'custom_admin/kyc_review.html', context)


@login_required
@user_passes_test(is_admin)
def kyc_approve(request, user_id):
    """Approve KYC for a user"""
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    
    if profile.kyc_status != 'verified':
        profile.kyc_status = 'verified'
        profile.kyc_reviewed_at = timezone.now()
        profile.kyc_reviewed_by = request.user
        profile.kyc_rejection_reason = None
        profile.is_verified = True
        profile.save()
        
        messages.success(request, f'KYC approved for {user.username}. User is now verified.')
    else:
        messages.info(request, f'KYC for {user.username} is already verified.')
    
    return redirect('custom_admin:kyc_requests_list')


@login_required
@user_passes_test(is_admin)
def kyc_reject(request, user_id):
    """Reject KYC for a user"""
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        
        if not rejection_reason:
            messages.error(request, 'Please provide a reason for rejection.')
            return redirect('custom_admin:kyc_review', user_id=user_id)
        
        profile.kyc_status = 'rejected'
        profile.kyc_reviewed_at = timezone.now()
        profile.kyc_reviewed_by = request.user
        profile.kyc_rejection_reason = rejection_reason
        profile.is_verified = False
        profile.save()
        
        messages.success(request, f'KYC rejected for {user.username}. User can resubmit documents.')
        return redirect('custom_admin:kyc_requests_list')
    
    return redirect('custom_admin:kyc_review', user_id=user_id)


# ========================
# Currency Management Views
# ========================

@login_required
@user_passes_test(is_admin)
def currencies_list(request):
    """List all currencies"""
    from transactions.currency_models import Currency
    
    currencies = Currency.objects.all().order_by('display_order', 'code')
    
    context = {
        'currencies': currencies,
        'total_currencies': currencies.count(),
        'active_currencies': currencies.filter(is_active=True).count(),
    }
    
    return render(request, 'custom_admin/currencies_list.html', context)


@login_required
@user_passes_test(is_admin)
def currency_create(request):
    """Create a new currency"""
    from transactions.currency_models import Currency
    from transactions.currency_utils import CurrencyManager
    
    if request.method == 'POST':
        try:
            currency = Currency.objects.create(
                code=request.POST.get('code').upper(),
                name=request.POST.get('name'),
                symbol=request.POST.get('symbol'),
                symbol_position=request.POST.get('symbol_position', 'before'),
                decimal_places=int(request.POST.get('decimal_places', 2)),
                thousand_separator=request.POST.get('thousand_separator', ','),
                decimal_separator=request.POST.get('decimal_separator', '.'),
                is_active=request.POST.get('is_active') == 'on',
                is_base_currency=request.POST.get('is_base_currency') == 'on',
                display_order=int(request.POST.get('display_order', 0))
            )
            CurrencyManager.clear_cache()
            messages.success(request, f'Currency {currency.code} created successfully.')
            return redirect('custom_admin:currencies_list')
        except Exception as e:
            messages.error(request, f'Error creating currency: {str(e)}')
    
    return render(request, 'custom_admin/currency_form.html', {'mode': 'create'})


@login_required
@user_passes_test(is_admin)
def currency_edit(request, currency_id):
    """Edit an existing currency"""
    from transactions.currency_models import Currency
    from transactions.currency_utils import CurrencyManager
    
    currency = get_object_or_404(Currency, id=currency_id)
    
    if request.method == 'POST':
        try:
            currency.code = request.POST.get('code').upper()
            currency.name = request.POST.get('name')
            currency.symbol = request.POST.get('symbol')
            currency.symbol_position = request.POST.get('symbol_position', 'before')
            currency.decimal_places = int(request.POST.get('decimal_places', 2))
            currency.thousand_separator = request.POST.get('thousand_separator', ',')
            currency.decimal_separator = request.POST.get('decimal_separator', '.')
            currency.is_active = request.POST.get('is_active') == 'on'
            currency.is_base_currency = request.POST.get('is_base_currency') == 'on'
            currency.display_order = int(request.POST.get('display_order', 0))
            currency.save()
            
            CurrencyManager.clear_cache()
            messages.success(request, f'Currency {currency.code} updated successfully.')
            return redirect('custom_admin:currencies_list')
        except Exception as e:
            messages.error(request, f'Error updating currency: {str(e)}')
    
    context = {
        'mode': 'edit',
        'currency': currency,
    }
    
    return render(request, 'custom_admin/currency_form.html', context)


@login_required
@user_passes_test(is_admin)
def currency_toggle_status(request, currency_id):
    """Toggle currency active status"""
    from transactions.currency_models import Currency
    from transactions.currency_utils import CurrencyManager
    
    currency = get_object_or_404(Currency, id=currency_id)
    currency.is_active = not currency.is_active
    currency.save()
    
    CurrencyManager.clear_cache()
    
    status = 'activated' if currency.is_active else 'deactivated'
    messages.success(request, f'Currency {currency.code} has been {status}.')
    
    return redirect('custom_admin:currencies_list')


@login_required
@user_passes_test(is_admin)
def exchange_rates_list(request):
    """List all exchange rates"""
    from transactions.currency_models import ExchangeRate, Currency
    
    # Get filter parameters
    from_currency_code = request.GET.get('from_currency')
    to_currency_code = request.GET.get('to_currency')
    is_active = request.GET.get('is_active')
    
    rates = ExchangeRate.objects.select_related('from_currency', 'to_currency').all()
    
    # Apply filters
    if from_currency_code:
        rates = rates.filter(from_currency__code=from_currency_code)
    if to_currency_code:
        rates = rates.filter(to_currency__code=to_currency_code)
    if is_active:
        rates = rates.filter(is_active=is_active == 'true')
    
    rates = rates.order_by('-effective_from')
    
    # Get all currencies for filter dropdown
    currencies = Currency.objects.filter(is_active=True).order_by('code')
    
    context = {
        'rates': rates,
        'currencies': currencies,
        'total_rates': rates.count(),
        'active_rates': rates.filter(is_active=True).count(),
    }
    
    return render(request, 'custom_admin/exchange_rates_list.html', context)


@login_required
@user_passes_test(is_admin)
def exchange_rate_create(request):
    """Create a new exchange rate"""
    from transactions.currency_models import ExchangeRate, Currency
    from transactions.currency_utils import CurrencyManager
    from decimal import Decimal
    
    if request.method == 'POST':
        try:
            from_currency = get_object_or_404(Currency, id=request.POST.get('from_currency'))
            to_currency = get_object_or_404(Currency, id=request.POST.get('to_currency'))
            
            if from_currency == to_currency:
                messages.error(request, 'From and To currencies cannot be the same.')
                return redirect('custom_admin:exchange_rate_create')
            
            rate = ExchangeRate.objects.create(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=Decimal(request.POST.get('rate')),
                source=f'manual_by_{request.user.username}',
                is_active=request.POST.get('is_active') == 'on',
                effective_from=timezone.now()
            )
            
            CurrencyManager.clear_cache()
            messages.success(request, f'Exchange rate from {from_currency.code} to {to_currency.code} created successfully.')
            return redirect('custom_admin:exchange_rates_list')
        except Exception as e:
            messages.error(request, f'Error creating exchange rate: {str(e)}')
    
    currencies = Currency.objects.filter(is_active=True).order_by('code')
    context = {
        'mode': 'create',
        'currencies': currencies,
    }
    
    return render(request, 'custom_admin/exchange_rate_form.html', context)


@login_required
@user_passes_test(is_admin)
def exchange_rate_edit(request, rate_id):
    """Edit an existing exchange rate"""
    from transactions.currency_models import ExchangeRate, Currency
    from transactions.currency_utils import CurrencyManager
    from decimal import Decimal
    
    rate_obj = get_object_or_404(ExchangeRate, id=rate_id)
    
    if request.method == 'POST':
        try:
            rate_obj.rate = Decimal(request.POST.get('rate'))
            rate_obj.is_active = request.POST.get('is_active') == 'on'
            rate_obj.save()
            
            CurrencyManager.clear_cache()
            messages.success(request, f'Exchange rate updated successfully.')
            return redirect('custom_admin:exchange_rates_list')
        except Exception as e:
            messages.error(request, f'Error updating exchange rate: {str(e)}')
    
    currencies = Currency.objects.filter(is_active=True).order_by('code')
    context = {
        'mode': 'edit',
        'rate': rate_obj,
        'currencies': currencies,
    }
    
    return render(request, 'custom_admin/exchange_rate_form.html', context)


@login_required
@user_passes_test(is_admin)
def exchange_rate_delete(request, rate_id):
    """Delete an exchange rate"""
    from transactions.currency_models import ExchangeRate
    from transactions.currency_utils import CurrencyManager
    
    rate = get_object_or_404(ExchangeRate, id=rate_id)
    from_code = rate.from_currency.code
    to_code = rate.to_currency.code
    rate.delete()
    
    CurrencyManager.clear_cache()
    messages.success(request, f'Exchange rate from {from_code} to {to_code} has been deleted.')
    
    return redirect('custom_admin:exchange_rates_list')


@login_required
@user_passes_test(is_admin)
def refresh_exchange_rates(request):
    """Refresh exchange rates from live API"""
    from transactions.currency_utils import update_exchange_rates_from_api, CurrencyManager
    
    result = update_exchange_rates_from_api()
    
    if result['success']:
        # Build success message with updated rates
        updated_list = ', '.join([f"{item['currency']} ({item['symbol']}{item['rate']:.2f})" 
                                  for item in result['updated'][:5]])  # Show first 5
        if len(result['updated']) > 5:
            updated_list += f" and {len(result['updated']) - 5} more"
        
        messages.success(request, f'✓ Exchange rates updated successfully! {updated_list}')
        
        if result['failed']:
            failed_list = ', '.join([item['currency'] for item in result['failed']])
            messages.warning(request, f'Failed to update: {failed_list}')
    else:
        messages.error(request, f'Failed to update exchange rates: {result["message"]}')
    
    # Clear cache
    CurrencyManager.clear_cache()
    
    return redirect('custom_admin:exchange_rates_list')