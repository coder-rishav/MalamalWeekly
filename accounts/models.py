from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with wallet and additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=100, default='India')
    
    # Wallet
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_deposits = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_withdrawals = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_winnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Account status
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True, null=True)
    blocked_at = models.DateTimeField(null=True, blank=True)
    blocked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='blocked_users')
    
    # User Permissions - Granular Control
    can_play_games = models.BooleanField(default=True, help_text="Allow user to participate in games")
    can_deposit = models.BooleanField(default=True, help_text="Allow user to make deposit requests")
    can_withdraw = models.BooleanField(default=True, help_text="Allow user to make withdrawal requests")
    can_view_games = models.BooleanField(default=True, help_text="Allow user to view game pages")
    can_view_leaderboard = models.BooleanField(default=True, help_text="Allow user to view leaderboard")
    can_view_transaction_history = models.BooleanField(default=True, help_text="Allow user to view transaction history")
    can_edit_profile = models.BooleanField(default=True, help_text="Allow user to edit profile")
    
    # Restriction Notes
    restriction_notes = models.TextField(blank=True, null=True, help_text="Admin notes about user restrictions")
    last_permission_change = models.DateTimeField(null=True, blank=True)
    permission_changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='permission_changes')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def add_credits(self, amount):
        """Add credits to user wallet"""
        self.wallet_balance += amount
        self.total_deposits += amount
        self.save()
    
    def deduct_credits(self, amount):
        """Deduct credits from user wallet"""
        if self.wallet_balance >= amount:
            self.wallet_balance -= amount
            self.total_spent += amount
            self.save()
            return True
        return False
    
    def add_winnings(self, amount):
        """Add winning amount to wallet"""
        self.wallet_balance += amount
        self.total_winnings += amount
        self.save()


class BanAppeal(models.Model):
    """Model for users to appeal their ban - one time only"""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ban_appeal')
    appeal_message = models.TextField(help_text="User's appeal message")
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_appeals')
    admin_response = models.TextField(blank=True, null=True, help_text="Admin's response to the appeal")
    
    class Meta:
        verbose_name = 'Ban Appeal'
        verbose_name_plural = 'Ban Appeals'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Appeal by {self.user.username} - {self.status}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
