from django.core.management.base import BaseCommand
from transactions.currency_utils import initialize_default_currencies, set_exchange_rates_to_inr


class Command(BaseCommand):
    help = 'Initialize default currencies and exchange rates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-rates',
            action='store_true',
            help='Also initialize exchange rates',
        )

    def handle(self, *args, **options):
        self.stdout.write('Initializing default currencies...')
        
        created_currencies = initialize_default_currencies()
        
        if created_currencies:
            self.stdout.write(self.style.SUCCESS(f'Created {len(created_currencies)} currencies:'))
            for currency in created_currencies:
                self.stdout.write(f'  - {currency.code}: {currency.name}')
        else:
            self.stdout.write(self.style.WARNING('All currencies already exist'))
        
        if options['with_rates']:
            self.stdout.write('\nInitializing exchange rates...')
            created_rates = set_exchange_rates_to_inr()
            
            if created_rates:
                self.stdout.write(self.style.SUCCESS(f'Created {len(created_rates)} exchange rates'))
            else:
                self.stdout.write(self.style.WARNING('Exchange rates already exist'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Currency initialization complete!'))
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Run migrations if you haven\'t: python manage.py makemigrations && python manage.py migrate')
        self.stdout.write('2. Update exchange rates in admin panel or via API')
        self.stdout.write('3. Set user currency preferences')
