from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, UserUpdateForm
from .models import UserProfile
from games.models import Leaderboard
from transactions.models import Transaction


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('games:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create leaderboard entry for new user
            Leaderboard.objects.create(user=user)
            
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            return redirect('games:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('games:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Ensure user has a profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # Allow login even if blocked, but redirect to banned page
                login(request, user)
                
                if profile.is_blocked:
                    return redirect('accounts:account_banned')
                
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'games:dashboard')
                return redirect(next_url)
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def account_banned(request):
    """Show banned account page with appeal option"""
    profile = request.user.profile
    
    # Check if user has already submitted an appeal
    from .models import BanAppeal
    existing_appeal = BanAppeal.objects.filter(user=request.user).first()
    
    if request.method == 'POST' and not existing_appeal:
        appeal_message = request.POST.get('appeal_message', '').strip()
        
        if appeal_message:
            # Create new appeal
            BanAppeal.objects.create(
                user=request.user,
                appeal_message=appeal_message
            )
            messages.success(request, 'Your appeal has been submitted successfully. Our team will review it soon.')
        else:
            messages.error(request, 'Please provide a message for your appeal.')
    
    context = {
        'reason': profile.blocked_reason if profile.is_blocked else 'Account suspended',
        'existing_appeal': existing_appeal,
    }
    return render(request, 'accounts/account_banned.html', context)


@login_required
def profile(request):
    """User profile view"""
    user = request.user
    
    # Ensure user has a profile (create if missing)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get user statistics
    total_entries = user.game_entries.count()
    total_wins = user.game_entries.filter(is_winner=True).count()
    win_rate = (total_wins / total_entries * 100) if total_entries > 0 else 0
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:10]
    
    # Get leaderboard position
    try:
        leaderboard = Leaderboard.objects.get(user=user)
    except Leaderboard.DoesNotExist:
        leaderboard = Leaderboard.objects.create(user=user)
    
    context = {
        'profile': profile,
        'total_entries': total_entries,
        'total_wins': total_wins,
        'win_rate': round(win_rate, 2),
        'recent_transactions': recent_transactions,
        'leaderboard': leaderboard,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile view"""
    # Ensure user has a profile (create if missing)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'accounts/edit_profile.html', context)
