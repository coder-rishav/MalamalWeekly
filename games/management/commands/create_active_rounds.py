from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from games.models import Game, GameRound


class Command(BaseCommand):
    help = 'Create active rounds for all games'

    def handle(self, *args, **kwargs):
        games = Game.objects.filter(status='active')
        
        if not games.exists():
            self.stdout.write(self.style.ERROR('No active games found. Run create_initial_games first.'))
            return
        
        created_count = 0
        
        for game in games:
            # Check if game already has an open round
            existing_open = game.rounds.filter(status='open').exists()
            
            if existing_open:
                self.stdout.write(self.style.WARNING(f'{game.name} already has an open round'))
                continue
            
            # Get the last round number
            last_round = game.rounds.order_by('-round_number').first()
            next_round_number = (last_round.round_number + 1) if last_round else 1
            
            # Create new round
            now = timezone.now()
            game_round = GameRound.objects.create(
                game=game,
                round_number=next_round_number,
                scheduled_start=now,
                scheduled_end=now + timedelta(days=7),  # 7 days from now
                actual_start=now,
                status='open'
            )
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Created Round #{game_round.round_number} for {game.name} (ends in 7 days)'
                )
            )
        
        if created_count == 0:
            self.stdout.write(self.style.WARNING('No new rounds created. All games already have active rounds.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Successfully created {created_count} active round(s)!')
            )
