from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from games.models import Leaderboard


class Command(BaseCommand):
    help = 'Creates missing profiles and leaderboard entries for existing users'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        profiles_created = 0
        leaderboards_created = 0
        
        for user in users:
            # Create profile if missing
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                profiles_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created profile for user: {user.username}'))
            
            # Create leaderboard entry if missing
            leaderboard, created = Leaderboard.objects.get_or_create(user=user)
            if created:
                leaderboards_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created leaderboard entry for user: {user.username}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Summary:'))
        self.stdout.write(self.style.SUCCESS(f'   - Total users: {users.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   - Profiles created: {profiles_created}'))
        self.stdout.write(self.style.SUCCESS(f'   - Leaderboard entries created: {leaderboards_created}'))
        
        if profiles_created == 0 and leaderboards_created == 0:
            self.stdout.write(self.style.SUCCESS('\n✅ All users already have profiles and leaderboard entries!'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Missing profiles and leaderboard entries have been created!'))
