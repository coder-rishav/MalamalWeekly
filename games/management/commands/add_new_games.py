from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from games.models import Game


class Command(BaseCommand):
    help = 'Add Keno and Odd/Even games to the system'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()
        
        # Create Keno game
        keno_game, created = Game.objects.get_or_create(
            name='Keno Master',
            defaults={
                'game_type': 'keno',
                'description': 'Pick up to 20 numbers from 1-80 and watch the draw! More matches = bigger wins!',
                'rules': '''How to Play Keno:
1. Choose between 1 to 20 numbers from the grid (1-80)
2. Select your bet amount
3. Wait for the draw - 20 random numbers will be selected
4. Win based on how many of your numbers match!

Winning Combinations:
- 1 number picked: Match 1 = 3x your bet
- 2 numbers picked: Match 2 = 12x your bet
- 3 numbers picked: Match 2 = 2x, Match 3 = 25x
- 4 numbers picked: Match 2 = 1x, Match 3 = 5x, Match 4 = 75x
- 5 numbers picked: Match 3 = 2x, Match 4 = 15x, Match 5 = 250x
- 6 numbers picked: Match 3 = 1x, Match 4 = 5x, Match 5 = 75x, Match 6 = 1000x
- 7 numbers picked: Match 4 = 2x, Match 5 = 25x, Match 6 = 250x, Match 7 = 2500x
- 8 numbers picked: Match 5 = 10x, Match 6 = 75x, Match 7 = 500x, Match 8 = 5000x
- 9-10 numbers: Higher multipliers for more matches!

Tips:
- Picking more numbers gives higher potential wins
- But requires more matches to win
- Start with 5-7 numbers for balanced gameplay''',
                'entry_fee': 0.50,
                'min_participants': 1,
                'max_participants': 5000,
                'winning_amount': 100.00,
                'game_config': {
                    'number_pool': 80,
                    'min_pick': 1,
                    'max_pick': 20,
                    'numbers_drawn': 20,
                    'payout_table': {
                        '1': {'1': 3.0},
                        '2': {'2': 12.0},
                        '3': {'2': 2.0, '3': 25.0},
                        '4': {'2': 1.0, '3': 5.0, '4': 75.0},
                        '5': {'3': 2.0, '4': 15.0, '5': 250.0},
                        '6': {'3': 1.0, '4': 5.0, '5': 75.0, '6': 1000.0},
                        '7': {'4': 2.0, '5': 25.0, '6': 250.0, '7': 2500.0},
                        '8': {'5': 10.0, '6': 75.0, '7': 500.0, '8': 5000.0},
                        '9': {'5': 5.0, '6': 25.0, '7': 150.0, '8': 1000.0, '9': 7500.0},
                        '10': {'5': 2.0, '6': 20.0, '7': 100.0, '8': 500.0, '9': 2500.0, '10': 10000.0}
                    }
                },
                'status': 'active',
                'is_featured': True,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created Keno Master game'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Keno Master game already exists'))

        # Create Odd/Even game
        oddeven_game, created = Game.objects.get_or_create(
            name='Odd or Even Rush',
            defaults={
                'game_type': 'odd_even',
                'description': 'Will the next number be Odd or Even? Make your prediction and win instantly!',
                'rules': '''How to Play Odd or Even Rush:
1. A random number between 1-100 will be drawn
2. Before the draw, predict if it will be:
   - ODD (1, 3, 5, 7, ... 97, 99)
   - EVEN (2, 4, 6, 8, ... 98, 100)

Payouts:
- Correct ODD prediction: 1.95x your bet
- Correct EVEN prediction: 1.95x your bet
- Wrong prediction: Lose your bet

Special Rules:
- 50 numbers are odd (1-99)
- 50 numbers are even (2-100)
- Fair 50/50 chance!
- Instant results - no waiting!

Tips:
- Quick and simple gameplay
- Perfect for fast rounds
- Low house edge (2.5%)
- Great for beginners!''',
                'entry_fee': 0.10,
                'min_participants': 1,
                'max_participants': 10000,
                'winning_amount': 0.195,
                'game_config': {
                    'number_range': [1, 100],
                    'odd_payout': 1.95,
                    'even_payout': 1.95,
                    'choices': ['odd', 'even'],
                    'result_format': 'instant'
                },
                'status': 'active',
                'is_featured': False,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created Odd or Even Rush game'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Odd or Even Rush game already exists'))

        self.stdout.write(self.style.SUCCESS('\n🎮 Game setup complete!'))
        self.stdout.write(self.style.SUCCESS('Total games in system: {}'.format(Game.objects.count())))
