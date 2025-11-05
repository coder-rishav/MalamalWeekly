from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Game(models.Model):
    """Game definition with rules and settings"""
    GAME_TYPES = [
        ('number_match', 'Number Match'),
        ('lucky_draw', 'Lucky Draw'),
        ('color_game', 'Color Game'),
        ('keno', 'Keno'),
        ('odd_even', 'Odd/Even'),
        ('custom', 'Custom Game'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]
    
    name = models.CharField(max_length=200)
    game_type = models.CharField(max_length=50, choices=GAME_TYPES)
    description = models.TextField()
    rules = models.TextField(help_text="Game rules and instructions")
    image = models.ImageField(upload_to='games/', blank=True, null=True)
    
    # Game settings
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, help_text="Credits required to participate")
    min_participants = models.IntegerField(default=2, help_text="Minimum participants required")
    max_participants = models.IntegerField(default=1000, help_text="Maximum participants allowed")
    winning_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prize amount for winner")
    
    # Game configuration (stored as JSON)
    game_config = models.JSONField(
        default=dict,
        help_text="Game-specific configuration like number range, colors, etc."
    )
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    total_rounds_played = models.IntegerField(default=0)
    total_winners = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_games')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return self.name
    
    def get_active_round(self):
        """Get current active round for this game"""
        return self.rounds.filter(status='open').first()


class GameRound(models.Model):
    """Individual round/session of a game"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('open', 'Open for Entry'),
        ('closed', 'Entry Closed'),
        ('processing', 'Processing Results'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField()
    
    # Timing
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Round details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    total_participants = models.IntegerField(default=0)
    total_pool_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Results
    winning_combination = models.JSONField(null=True, blank=True, help_text="Winning numbers/colors/etc")
    has_winner = models.BooleanField(default=False)
    result_announced_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='initiated_rounds')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Game Round'
        verbose_name_plural = 'Game Rounds'
        ordering = ['-scheduled_start']
        unique_together = ['game', 'round_number']
    
    def __str__(self):
        return f"{self.game.name} - Round {self.round_number}"
    
    def is_open_for_entry(self):
        """Check if round is accepting entries"""
        now = timezone.now()
        return (
            self.status == 'open' and
            self.scheduled_start <= now < self.scheduled_end and
            self.total_participants < self.game.max_participants
        )
    
    def can_participate(self, user):
        """Check if user can participate in this round"""
        if not self.is_open_for_entry():
            return False, "Round is not open for entry"
        
        # Check if user already participated
        if self.entries.filter(user=user).exists():
            return False, "You have already entered this round"
        
        # Check if user has enough credits
        if user.profile.wallet_balance < self.game.entry_fee:
            return False, "Insufficient credits"
        
        return True, "OK"


class UserEntry(models.Model):
    """User's entry/participation in a game round"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_entries')
    game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE, related_name='entries')
    
    # User's choice/selection
    user_choice = models.JSONField(help_text="User's selected numbers/colors/etc")
    
    # Entry details
    entry_fee_paid = models.DecimalField(max_digits=10, decimal_places=2)
    is_winner = models.BooleanField(default=False)
    winning_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prize_claimed = models.BooleanField(default=False)
    prize_claimed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    entry_number = models.CharField(max_length=50, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Entry'
        verbose_name_plural = 'User Entries'
        ordering = ['-created_at']
        unique_together = ['user', 'game_round']
    
    def __str__(self):
        return f"{self.user.username} - {self.game_round}"
    
    def save(self, *args, **kwargs):
        if not self.entry_number:
            # Generate unique entry number
            import uuid
            self.entry_number = f"ENT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class Winner(models.Model):
    """Winner records for each game round"""
    game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE, related_name='winners')
    user_entry = models.OneToOneField(UserEntry, on_delete=models.CASCADE, related_name='winner_record')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winnings')
    
    # Prize details
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2)
    prize_credited = models.BooleanField(default=False)
    prize_credited_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    announced_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Winner'
        verbose_name_plural = 'Winners'
        ordering = ['-announced_at']
    
    def __str__(self):
        return f"{self.user.username} won {self.prize_amount} in {self.game_round}"


class Leaderboard(models.Model):
    """Leaderboard/rankings for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='leaderboard')
    
    # Statistics
    total_games_played = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_winnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    win_rate = models.FloatField(default=0.0)
    
    # Ranking
    rank = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(default=0)
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Leaderboard Entry'
        verbose_name_plural = 'Leaderboard'
        ordering = ['-points', '-total_winnings']
    
    def __str__(self):
        return f"{self.user.username} - Rank: {self.rank or 'Unranked'}"
    
    def update_stats(self):
        """Update user statistics"""
        entries = UserEntry.objects.filter(user=self.user)
        self.total_games_played = entries.count()
        self.total_wins = entries.filter(is_winner=True).count()
        self.total_winnings = sum(entry.winning_amount for entry in entries.filter(is_winner=True))
        self.total_spent = sum(entry.entry_fee_paid for entry in entries)
        self.win_rate = (self.total_wins / self.total_games_played * 100) if self.total_games_played > 0 else 0
        self.points = (self.total_wins * 10) + int(self.total_winnings)
        self.save()
