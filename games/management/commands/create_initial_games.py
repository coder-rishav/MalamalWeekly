from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from games.models import Game


class Command(BaseCommand):
    help = 'Creates initial game data with 3 different game types'

    def handle(self, *args, **kwargs):
        # Get or create admin user for created_by field
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@malamalweekly.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user: admin / admin123'))
        
        # Game 1: Number Match
        game1, created = Game.objects.get_or_create(
            name='Lucky Number Match',
            defaults={
                'game_type': 'number_match',
                'description': 'Choose 5 numbers between 0-99. Match all 5 numbers in the EXACT sequence to win!',
                'rules': '''
HOW TO PLAY:
1. Select 5 unique numbers between 0 and 99
2. Numbers must be in sequence
3. Match all 5 numbers in exact order to win
4. Example: If you choose [12, 45, 67, 23, 89] and winning numbers are [12, 45, 67, 23, 89], you WIN!
5. If even one number is out of sequence, you don't win
6. Game rounds run weekly
                ''',
                'entry_fee': 50.00,
                'min_participants': 2,
                'max_participants': 1000,
                'winning_amount': 10000.00,
                'game_config': {
                    'number_count': 5,
                    'min_number': 0,
                    'max_number': 99,
                    'allow_duplicates': False,
                    'sequence_matters': True
                },
                'status': 'active',
                'is_featured': True,
                'created_by': admin_user
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created game: Lucky Number Match'))
        
        # Game 2: Lucky Draw
        game2, created = Game.objects.get_or_create(
            name='Super Lucky Draw',
            defaults={
                'game_type': 'lucky_draw',
                'description': 'Pick your lucky number between 1-100. Match the winning number to win big!',
                'rules': '''
HOW TO PLAY:
1. Choose ONE number between 1 and 100
2. If your number matches the randomly drawn winning number, you WIN!
3. Simple and straightforward
4. Game runs daily
5. Multiple winners possible if same number is chosen
                ''',
                'entry_fee': 20.00,
                'min_participants': 5,
                'max_participants': 500,
                'winning_amount': 5000.00,
                'game_config': {
                    'number_count': 1,
                    'min_number': 1,
                    'max_number': 100,
                    'allow_duplicates': False,
                    'sequence_matters': False
                },
                'status': 'active',
                'is_featured': True,
                'created_by': admin_user
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created game: Super Lucky Draw'))
        
        # Game 3: Color Game
        game3, created = Game.objects.get_or_create(
            name='Color Prediction',
            defaults={
                'game_type': 'color_game',
                'description': 'Predict the winning color! Choose from Red, Green, Blue, or Yellow.',
                'rules': '''
HOW TO PLAY:
1. Select ONE color: Red, Green, Blue, or Yellow
2. Admin will randomly select the winning color
3. Match the winning color to win!
4. Fast-paced and exciting
5. Rounds every few hours
                ''',
                'entry_fee': 10.00,
                'min_participants': 2,
                'max_participants': 2000,
                'winning_amount': 2000.00,
                'game_config': {
                    'colors': ['red', 'green', 'blue', 'yellow'],
                    'selection_count': 1
                },
                'status': 'active',
                'is_featured': False,
                'created_by': admin_user
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created game: Color Prediction'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ All games created successfully!'))
        self.stdout.write(self.style.WARNING('\nNext steps:'))
        self.stdout.write('1. Create a superuser if you haven\'t: python manage.py createsuperuser')
        self.stdout.write('2. Run the server: python manage.py runserver')
        self.stdout.write('3. Access admin panel: http://127.0.0.1:8000/admin/')
        self.stdout.write('4. Create game rounds from admin panel')
