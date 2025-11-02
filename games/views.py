from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum
from django.http import JsonResponse
from .models import Game, GameRound, UserEntry, Winner, Leaderboard
from transactions.models import Transaction
import json


def home(request):
    """Landing page"""
    if request.user.is_authenticated:
        return redirect('games:dashboard')
    
    featured_games = Game.objects.filter(status='active', is_featured=True)[:3]
    recent_winners = Winner.objects.all().order_by('-announced_at')[:5]
    
    context = {
        'featured_games': featured_games,
        'recent_winners': recent_winners,
    }
    return render(request, 'games/home.html', context)


@login_required
def dashboard(request):
    """User dashboard"""
    user = request.user
    
    # Ensure user has a profile (create if missing)
    from accounts.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get active games only if user has permission
    active_games = Game.objects.none()  # Empty queryset by default
    upcoming_rounds = GameRound.objects.none()  # Empty queryset by default
    
    if profile.can_view_games:
        active_games = Game.objects.filter(status='active')
        upcoming_rounds = GameRound.objects.filter(
            status='open',
            scheduled_end__gt=timezone.now()
        ).order_by('scheduled_end')[:5]
    
    # Get user's recent entries (always show their own entries)
    recent_entries = UserEntry.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Get user's winnings (always show their own winnings)
    my_winnings = Winner.objects.filter(user=user).order_by('-announced_at')[:5]
    
    context = {
        'profile': profile,
        'active_games': active_games,
        'recent_entries': recent_entries,
        'my_winnings': my_winnings,
        'upcoming_rounds': upcoming_rounds,
    }
    return render(request, 'games/dashboard.html', context)


@login_required
def games_list(request):
    """List all available games"""
    # Check permission
    profile = request.user.profile
    if not profile.can_view_games:
        messages.error(request, 'You do not have permission to view games.')
        return redirect('games:dashboard')
    
    games = Game.objects.filter(status='active').order_by('-is_featured', 'name')
    
    context = {
        'games': games,
    }
    return render(request, 'games/games_list.html', context)


@login_required
def game_detail(request, game_id):
    """Game details and play interface"""
    # Check permission to view games
    profile = request.user.profile
    if not profile.can_view_games:
        messages.error(request, 'You do not have permission to view games.')
        return redirect('games:dashboard')
    
    game = get_object_or_404(Game, id=game_id)
    
    # Get active round for this game
    active_round = game.get_active_round()
    
    # Get recent winners for this game
    recent_winners = Winner.objects.filter(
        game_round__game=game
    ).order_by('-announced_at')[:10]
    
    # Check if user already participated in active round
    user_entry = None
    if active_round:
        user_entry = UserEntry.objects.filter(
            user=request.user,
            game_round=active_round
        ).first()
    
    context = {
        'game': game,
        'active_round': active_round,
        'recent_winners': recent_winners,
        'user_entry': user_entry,
    }
    return render(request, 'games/game_detail.html', context)


@login_required
def play_game(request, game_id, round_id):
    """Handle game entry submission"""
    # Ensure user has a profile (create if missing)
    from accounts.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Check if user is blocked
    if profile.is_blocked:
        messages.error(request, f'Your account has been banned. Reason: {profile.blocked_reason}')
        return redirect('games:dashboard')
    
    # Check if user has permission to view games
    if not profile.can_view_games:
        messages.error(request, 'You do not have permission to view games.')
        return redirect('games:dashboard')
    
    # Check if user has permission to play games
    if not profile.can_play_games:
        messages.error(request, 'You do not have permission to play games.')
        return redirect('games:dashboard')
    
    game = get_object_or_404(Game, id=game_id)
    game_round = get_object_or_404(GameRound, id=round_id, game=game)
    
    if request.method == 'POST':
        # Check if user can participate
        can_participate, message = game_round.can_participate(request.user)
        
        if not can_participate:
            messages.error(request, message)
            return redirect('games:game_detail', game_id=game_id)
        
        # Get user's choice based on game type
        try:
            if game.game_type == 'number_match':
                user_choice = [
                    int(request.POST.get(f'number_{i}', 0))
                    for i in range(1, 6)
                ]
                # Validate numbers
                if len(user_choice) != 5:
                    raise ValueError("Must select 5 numbers")
                if any(n < 0 or n > 99 for n in user_choice):
                    raise ValueError("Numbers must be between 0 and 99")
            
            elif game.game_type == 'lucky_draw':
                user_choice = [int(request.POST.get('number', 0))]
                if user_choice[0] < 1 or user_choice[0] > 100:
                    raise ValueError("Number must be between 1 and 100")
            
            elif game.game_type == 'color_game':
                user_choice = [request.POST.get('color', '').lower()]
                valid_colors = ['red', 'green', 'blue', 'yellow']
                if user_choice[0] not in valid_colors:
                    raise ValueError("Invalid color selection")
            
            elif game.game_type == 'custom':
                # Handle custom game inputs
                config = game.game_config
                user_choice = []
                
                if config.get('input_type') == 'number':
                    number_count = config.get('number_count', 1)
                    min_val = config.get('min_value', 1)
                    max_val = config.get('max_value', 100)
                    
                    for i in range(1, number_count + 1):
                        num = int(request.POST.get(f'custom_number_{i}', 0))
                        if num < min_val or num > max_val:
                            raise ValueError(f"Number must be between {min_val} and {max_val}")
                        user_choice.append(num)
                    
                    # Check duplicates if not allowed
                    if not config.get('allow_duplicates', False) and len(user_choice) != len(set(user_choice)):
                        raise ValueError("Duplicate numbers not allowed")
                
                elif config.get('input_type') == 'choice':
                    if config.get('multiple_selection', False):
                        # Multiple checkboxes
                        user_choice = request.POST.getlist('custom_choice')
                        selection_count = config.get('selection_count', 1)
                        if len(user_choice) != selection_count:
                            raise ValueError(f"Must select exactly {selection_count} option(s)")
                        # Validate choices
                        valid_choices = config.get('choices', [])
                        if not all(c in valid_choices for c in user_choice):
                            raise ValueError("Invalid choice selection")
                    else:
                        # Single select
                        choice = request.POST.get('custom_choice', '')
                        valid_choices = config.get('choices', [])
                        if choice not in valid_choices:
                            raise ValueError("Invalid choice selection")
                        user_choice = [choice]
                
                elif config.get('input_type') == 'text':
                    text = request.POST.get('custom_text', '').strip()
                    min_len = config.get('min_length', 1)
                    max_len = config.get('max_length', 100)
                    
                    if len(text) < min_len or len(text) > max_len:
                        raise ValueError(f"Text must be between {min_len} and {max_len} characters")
                    
                    if not config.get('case_sensitive', False):
                        text = text.lower()
                    
                    user_choice = [text]
                
                else:
                    raise ValueError("Invalid custom game configuration")
            
            else:
                raise ValueError("Invalid game type")
        
        except (ValueError, TypeError) as e:
            messages.error(request, f'Invalid input: {str(e)}')
            return redirect('games:game_detail', game_id=game_id)
        
        # Ensure user has a profile (create if missing)
        from accounts.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Deduct entry fee from user wallet
        if not profile.deduct_credits(game.entry_fee):
            messages.error(request, 'Insufficient credits in your wallet.')
            return redirect('games:game_detail', game_id=game_id)
        
        # Create user entry
        entry = UserEntry.objects.create(
            user=request.user,
            game_round=game_round,
            user_choice=user_choice,
            entry_fee_paid=game.entry_fee
        )
        
        # Create transaction record
        Transaction.objects.create(
            user=request.user,
            transaction_type='game_entry',
            amount=game.entry_fee,
            status='completed',
            balance_before=request.user.profile.wallet_balance + game.entry_fee,
            balance_after=request.user.profile.wallet_balance,
            description=f'Entry fee for {game.name} - Round {game_round.round_number}',
            game_entry=entry,
            completed_at=timezone.now()
        )
        
        # Update round statistics
        game_round.total_participants += 1
        game_round.total_pool_amount += game.entry_fee
        game_round.save()
        
        messages.success(request, f'Successfully entered {game.name}! Entry Number: {entry.entry_number}')
        return redirect('games:my_entries')
    
    return redirect('games:game_detail', game_id=game_id)


@login_required
def my_entries(request):
    """User's game entries"""
    entries = UserEntry.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'entries': entries,
    }
    return render(request, 'games/my_entries.html', context)


@login_required
def winners_list(request):
    """List of all winners"""
    winners = Winner.objects.all().order_by('-announced_at')
    
    context = {
        'winners': winners,
    }
    return render(request, 'games/winners_list.html', context)


@login_required
def leaderboard(request):
    """Leaderboard view"""
    leaderboards = Leaderboard.objects.all().order_by('rank')[:100]
    
    # Get current user's position
    try:
        user_leaderboard = Leaderboard.objects.get(user=request.user)
    except Leaderboard.DoesNotExist:
        user_leaderboard = Leaderboard.objects.create(user=request.user)
        user_leaderboard.update_stats()
    
    context = {
        'leaderboards': leaderboards,
        'user_leaderboard': user_leaderboard,
    }
    return render(request, 'games/leaderboard.html', context)
