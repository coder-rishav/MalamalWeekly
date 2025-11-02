from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import UserProfile
from games.models import Game, GameRound, UserEntry, Winner
from transactions.models import Transaction, DepositRequest, WithdrawalRequest
from django.contrib.auth.models import User


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
    
    # Recent activity
    recent_transactions = Transaction.objects.select_related('user').order_by('-created_at')[:10]
    recent_entries = UserEntry.objects.select_related('user', 'game_round__game').order_by('-created_at')[:10]
    
    # Active rounds
    active_rounds = GameRound.objects.filter(status='open').select_related('game').order_by('-scheduled_end')[:5]
    
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
