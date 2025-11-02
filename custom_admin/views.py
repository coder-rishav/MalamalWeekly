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
