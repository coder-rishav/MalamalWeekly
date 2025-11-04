from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from transactions.models import Transaction


class Command(BaseCommand):
    help = 'Mark old pending transactions as failed (cleanup orphaned transactions)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Mark transactions pending for more than X hours as failed (default: 24)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        
        # Calculate cutoff time
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        # Find old pending transactions
        old_pending = Transaction.objects.filter(
            status='pending',
            created_at__lt=cutoff_time
        )
        
        count = old_pending.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS(f'✓ No pending transactions older than {hours} hours found'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would mark {count} transaction(s) as failed:'))
            for txn in old_pending[:10]:  # Show first 10
                self.stdout.write(f'  - Transaction #{txn.id}: ₹{txn.amount} ({txn.transaction_type}) - Created: {txn.created_at}')
            if count > 10:
                self.stdout.write(f'  ... and {count - 10} more')
        else:
            # Update transactions
            updated = old_pending.update(
                status='failed',
                payment_status='Transaction expired - payment not completed within time limit'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully marked {updated} transaction(s) as failed (older than {hours} hours)'
                )
            )
            
            # Show some details
            self.stdout.write('\nCleaned up transactions:')
            for txn in Transaction.objects.filter(
                status='failed',
                payment_status='Transaction expired - payment not completed within time limit'
            )[:5]:
                self.stdout.write(
                    f'  - Transaction #{txn.id}: ₹{txn.amount} for {txn.user.username}'
                )
