from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Game, GameRound, UserEntry, Winner, Leaderboard
import random
import json


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_type', 'entry_fee', 'winning_amount', 'status', 'is_featured', 'total_rounds_played', 'created_at')
    list_filter = ('game_type', 'status', 'is_featured', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('status', 'is_featured', 'entry_fee', 'winning_amount')
    readonly_fields = ('total_rounds_played', 'total_winners', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'game_type', 'description', 'rules', 'image')
        }),
        ('Game Settings', {
            'fields': (
                ('entry_fee', 'winning_amount'),
                ('min_participants', 'max_participants'),
                'game_config'
            )
        }),
        ('Status', {
            'fields': ('status', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('total_rounds_played', 'total_winners'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new game
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class UserEntryInline(admin.TabularInline):
    model = UserEntry
    extra = 0
    can_delete = False
    readonly_fields = ('user', 'user_choice', 'entry_fee_paid', 'is_winner', 'winning_amount', 'entry_number', 'created_at')
    fields = ('user', 'user_choice', 'entry_fee_paid', 'is_winner', 'winning_amount', 'entry_number')
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(GameRound)
class GameRoundAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'game', 'status', 'scheduled_start', 'scheduled_end', 'total_participants', 'total_pool_amount', 'has_winner')
    list_filter = ('status', 'game', 'has_winner', 'scheduled_start')
    search_fields = ('game__name', 'round_number')
    readonly_fields = ('total_participants', 'total_pool_amount', 'actual_start', 'actual_end', 'result_announced_at', 'created_at', 'updated_at')
    inlines = [UserEntryInline]
    
    fieldsets = (
        ('Game Information', {
            'fields': ('game', 'round_number', 'status')
        }),
        ('Schedule', {
            'fields': (
                ('scheduled_start', 'scheduled_end'),
                ('actual_start', 'actual_end')
            )
        }),
        ('Participants & Pool', {
            'fields': ('total_participants', 'total_pool_amount')
        }),
        ('Results', {
            'fields': ('winning_combination', 'has_winner', 'result_announced_at')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['open_round', 'close_round', 'process_results', 'select_winner']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new round
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def open_round(self, request, queryset):
        updated = queryset.update(status='open', actual_start=timezone.now())
        self.message_user(request, f'{updated} round(s) opened for entry.')
    open_round.short_description = "Open selected rounds for entry"
    
    def close_round(self, request, queryset):
        updated = queryset.update(status='closed', actual_end=timezone.now())
        self.message_user(request, f'{updated} round(s) closed.')
    close_round.short_description = "Close selected rounds"
    
    def process_results(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} round(s) marked for processing.')
    process_results.short_description = "Process results for selected rounds"
    
    def select_winner(self, request, queryset):
        """Randomly select winner(s) for closed rounds"""
        winners_selected = 0
        for game_round in queryset.filter(status='closed'):
            # Get all entries for this round
            entries = list(game_round.entries.all())
            
            if not entries:
                continue
            
            # Generate winning combination based on game type
            game = game_round.game
            if game.game_type == 'number_match':
                winning_combination = [random.randint(0, 99) for _ in range(5)]
            elif game.game_type == 'lucky_draw':
                winning_combination = [random.randint(1, 100)]
            elif game.game_type == 'color_game':
                colors = ['red', 'green', 'blue', 'yellow']
                winning_combination = [random.choice(colors)]
            else:
                winning_combination = []
            
            game_round.winning_combination = winning_combination
            
            # Check for exact matches
            winner_entry = None
            for entry in entries:
                if entry.user_choice == winning_combination:
                    winner_entry = entry
                    break
            
            # 70% chance of having a winner if exact match found
            if winner_entry and random.random() < 0.7:
                winner_entry.is_winner = True
                winner_entry.winning_amount = game.winning_amount
                winner_entry.save()
                
                # Create winner record
                Winner.objects.create(
                    game_round=game_round,
                    user_entry=winner_entry,
                    user=winner_entry.user,
                    prize_amount=game.winning_amount,
                    prize_credited=True,
                    prize_credited_at=timezone.now()
                )
                
                # Credit winning amount to user
                winner_entry.user.profile.add_winnings(game.winning_amount)
                
                game_round.has_winner = True
                winners_selected += 1
            else:
                game_round.has_winner = False
            
            game_round.status = 'completed'
            game_round.result_announced_at = timezone.now()
            game_round.save()
            
            # Update game statistics
            game.total_rounds_played += 1
            if game_round.has_winner:
                game.total_winners += 1
            game.save()
        
        self.message_user(request, f'Results processed. {winners_selected} winner(s) selected.')
    select_winner.short_description = "Select winner for closed rounds"


@admin.register(UserEntry)
class UserEntryAdmin(admin.ModelAdmin):
    list_display = ('entry_number', 'user', 'game_round', 'user_choice', 'entry_fee_paid', 'is_winner', 'winning_amount', 'created_at')
    list_filter = ('is_winner', 'prize_claimed', 'created_at', 'game_round__game')
    search_fields = ('user__username', 'entry_number', 'game_round__game__name')
    readonly_fields = ('entry_number', 'entry_fee_paid', 'is_winner', 'winning_amount', 'prize_claimed', 'prize_claimed_at', 'created_at')
    
    fieldsets = (
        ('Entry Information', {
            'fields': ('entry_number', 'user', 'game_round')
        }),
        ('User Choice', {
            'fields': ('user_choice',)
        }),
        ('Payment', {
            'fields': ('entry_fee_paid',)
        }),
        ('Results', {
            'fields': ('is_winner', 'winning_amount', 'prize_claimed', 'prize_claimed_at')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        return False


@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'game_round', 'prize_amount', 'prize_credited', 'prize_credited_at', 'announced_at')
    list_filter = ('prize_credited', 'announced_at', 'game_round__game')
    search_fields = ('user__username', 'game_round__game__name')
    readonly_fields = ('game_round', 'user_entry', 'user', 'prize_amount', 'announced_at')
    
    fieldsets = (
        ('Winner Information', {
            'fields': ('user', 'game_round', 'user_entry')
        }),
        ('Prize Details', {
            'fields': ('prize_amount', 'prize_credited', 'prize_credited_at')
        }),
        ('Metadata', {
            'fields': ('announced_at',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('rank', 'user', 'points', 'total_wins', 'total_winnings', 'total_games_played', 'win_rate', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user', 'total_games_played', 'total_wins', 'total_winnings', 'total_spent', 'win_rate', 'points', 'last_updated')
    
    fieldsets = (
        ('User', {
            'fields': ('user', 'rank')
        }),
        ('Statistics', {
            'fields': (
                'points',
                ('total_games_played', 'total_wins'),
                ('total_winnings', 'total_spent'),
                'win_rate'
            )
        }),
        ('Metadata', {
            'fields': ('last_updated',)
        }),
    )
    
    actions = ['update_leaderboard']
    
    def has_add_permission(self, request):
        return False
    
    def update_leaderboard(self, request, queryset):
        for leaderboard in queryset:
            leaderboard.update_stats()
        
        # Update ranks
        all_leaderboards = Leaderboard.objects.all().order_by('-points', '-total_winnings')
        for idx, lb in enumerate(all_leaderboards, start=1):
            lb.rank = idx
            lb.save(update_fields=['rank'])
        
        self.message_user(request, 'Leaderboard updated successfully.')
    update_leaderboard.short_description = "Update selected leaderboard entries"


# Customize admin site headers
admin.site.site_header = "Malamal Weekly Admin"
admin.site.site_title = "Malamal Weekly Admin Portal"
admin.site.index_title = "Welcome to Malamal Weekly Administration"
