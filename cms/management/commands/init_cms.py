from django.core.management.base import BaseCommand
from cms.models import Page, SocialLink, SiteSettings


class Command(BaseCommand):
    help = 'Populate CMS with initial pages and settings'

    def handle(self, *args, **options):
        self.stdout.write('Creating initial CMS data...')
        
        # Create Site Settings
        settings, created = SiteSettings.objects.get_or_create(pk=1)
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Site settings created'))
        else:
            self.stdout.write(self.style.WARNING('Site settings already exist'))
        
        # Create Pages
        pages_data = [
            {
                'title': 'About Us',
                'slug': 'about-us',
                'content': '''
<h2>Welcome to Malamal Weekly</h2>
<p>Malamal Weekly is India's premier online lottery and gaming platform, offering exciting opportunities to win big while ensuring fairness, security, and transparency.</p>

<h3>Our Mission</h3>
<p>To provide a world-class gaming experience that combines entertainment with integrity, giving every player a fair chance to win.</p>

<h3>Why Choose Us?</h3>
<ul>
    <li><strong>Secure Platform:</strong> Your data and transactions are protected with industry-standard encryption</li>
    <li><strong>Fair Play:</strong> All draws are conducted transparently with verified random number generation</li>
    <li><strong>Quick Payouts:</strong> Win and get paid within 24-48 hours</li>
    <li><strong>24/7 Support:</strong> Our customer support team is always here to help</li>
</ul>

<h3>Our Values</h3>
<p>Integrity, Transparency, Responsibility, and Customer Satisfaction are at the core of everything we do.</p>
                ''',
                'meta_description': 'Learn about Malamal Weekly - India\'s trusted online lottery and gaming platform',
                'footer_section': 'information',
                'order': 1
            },
            {
                'title': 'How to Play',
                'slug': 'how-to-play',
                'content': '''
<h2>Getting Started with Malamal Weekly</h2>
<p>Playing on Malamal Weekly is easy and fun! Follow these simple steps:</p>

<h3>Step 1: Create Your Account</h3>
<p>Sign up with your email and create a secure password. Complete your profile to get started.</p>

<h3>Step 2: Add Credits</h3>
<p>Deposit funds securely using UPI, Net Banking, Credit/Debit Cards, or other payment methods.</p>

<h3>Step 3: Choose Your Game</h3>
<p>Browse our exciting range of lottery games and select the one you want to play.</p>

<h3>Step 4: Select Your Numbers</h3>
<p>Pick your lucky numbers or use our Quick Pick feature for random selection.</p>

<h3>Step 5: Confirm Your Entry</h3>
<p>Review your selections and confirm your entry. Credits will be deducted from your wallet.</p>

<h3>Step 6: Wait for Results</h3>
<p>Check the results when the draw is conducted. Winners are announced immediately!</p>

<h3>Step 7: Claim Your Prize</h3>
<p>If you win, your prize money is automatically credited to your wallet. Withdraw anytime!</p>

<h2>Tips for Playing</h2>
<ul>
    <li>Play responsibly and within your budget</li>
    <li>Check draw times before entering</li>
    <li>Use multiple entries to increase your chances</li>
    <li>Join our leaderboard competitions for bonus prizes</li>
</ul>
                ''',
                'meta_description': 'Learn how to play lottery games on Malamal Weekly',
                'footer_section': 'information',
                'order': 2
            },
            {
                'title': 'Terms & Conditions',
                'slug': 'terms-conditions',
                'content': '''
<h2>Terms and Conditions</h2>
<p><em>Last Updated: November 4, 2025</em></p>

<h3>1. Acceptance of Terms</h3>
<p>By accessing and using Malamal Weekly, you accept and agree to be bound by these Terms and Conditions.</p>

<h3>2. Eligibility</h3>
<p>You must be at least 18 years old to use our services. By registering, you confirm that you meet this age requirement.</p>

<h3>3. Account Responsibilities</h3>
<ul>
    <li>You are responsible for maintaining the confidentiality of your account credentials</li>
    <li>You must provide accurate and complete information</li>
    <li>One account per person is allowed</li>
    <li>Account sharing is strictly prohibited</li>
</ul>

<h3>4. Game Rules</h3>
<ul>
    <li>All games are subject to specific rules displayed on game pages</li>
    <li>Entries are final once submitted</li>
    <li>Draw results are final and binding</li>
</ul>

<h3>5. Payments and Withdrawals</h3>
<ul>
    <li>All transactions must be from accounts in your name</li>
    <li>Minimum deposit and withdrawal limits apply</li>
    <li>Withdrawals are processed within 24-48 hours</li>
    <li>We reserve the right to verify identity before processing withdrawals</li>
</ul>

<h3>6. Fair Play</h3>
<ul>
    <li>Cheating, collusion, or fraudulent activity will result in account termination</li>
    <li>We use certified random number generation for all draws</li>
    <li>Suspicious activity will be investigated</li>
</ul>

<h3>7. Limitation of Liability</h3>
<p>Malamal Weekly is not liable for any indirect, incidental, or consequential damages arising from your use of our services.</p>

<h3>8. Changes to Terms</h3>
<p>We reserve the right to modify these terms at any time. Continued use constitutes acceptance of modified terms.</p>

<h3>9. Governing Law</h3>
<p>These terms are governed by the laws of India.</p>
                ''',
                'meta_description': 'Read the Terms and Conditions of Malamal Weekly',
                'footer_section': 'information',
                'order': 3
            },
            {
                'title': 'Privacy Policy',
                'slug': 'privacy-policy',
                'content': '''
<h2>Privacy Policy</h2>
<p><em>Last Updated: November 4, 2025</em></p>

<h3>1. Information We Collect</h3>
<p>We collect the following types of information:</p>
<ul>
    <li><strong>Personal Information:</strong> Name, email, phone number, date of birth</li>
    <li><strong>Financial Information:</strong> Bank account details, payment card information</li>
    <li><strong>Usage Data:</strong> IP address, browser type, pages visited, time spent</li>
    <li><strong>Game Activity:</strong> Entries, wins, transaction history</li>
</ul>

<h3>2. How We Use Your Information</h3>
<ul>
    <li>To provide and improve our services</li>
    <li>To process transactions and payments</li>
    <li>To communicate important updates</li>
    <li>To comply with legal requirements</li>
    <li>To prevent fraud and ensure security</li>
</ul>

<h3>3. Information Sharing</h3>
<p>We do not sell your personal information. We may share data with:</p>
<ul>
    <li>Payment processors for transaction processing</li>
    <li>Service providers who assist our operations</li>
    <li>Legal authorities when required by law</li>
</ul>

<h3>4. Data Security</h3>
<p>We implement industry-standard security measures including:</p>
<ul>
    <li>SSL encryption for all data transmission</li>
    <li>Secure servers with restricted access</li>
    <li>Regular security audits</li>
    <li>PCI-DSS compliance for payment processing</li>
</ul>

<h3>5. Your Rights</h3>
<p>You have the right to:</p>
<ul>
    <li>Access your personal data</li>
    <li>Correct inaccurate information</li>
    <li>Request deletion of your data</li>
    <li>Opt-out of marketing communications</li>
    <li>Download your data</li>
</ul>

<h3>6. Cookies</h3>
<p>We use cookies to enhance your experience. You can control cookie settings in your browser.</p>

<h3>7. Changes to Privacy Policy</h3>
<p>We may update this policy from time to time. We will notify you of significant changes.</p>

<h3>8. Contact Us</h3>
<p>For privacy-related questions, contact us at: privacy@malamalweekly.com</p>
                ''',
                'meta_description': 'Read our Privacy Policy to understand how we protect your data',
                'footer_section': 'information',
                'order': 4
            },
            {
                'title': 'Responsible Gaming',
                'slug': 'responsible-gaming',
                'content': '''
<h2>Responsible Gaming</h2>
<p>At Malamal Weekly, we are committed to promoting responsible gaming and preventing problem gambling.</p>

<h3>Our Commitment</h3>
<p>We believe gaming should be entertainment, not a source of financial difficulty. We provide tools and resources to help you play responsibly.</p>

<h3>Tips for Responsible Gaming</h3>
<ul>
    <li><strong>Set a Budget:</strong> Decide how much you can afford to spend and stick to it</li>
    <li><strong>Set Time Limits:</strong> Don't let gaming interfere with daily responsibilities</li>
    <li><strong>Never Chase Losses:</strong> Accept losses as part of the entertainment cost</li>
    <li><strong>Take Breaks:</strong> Regular breaks help maintain perspective</li>
    <li><strong>Don't Gamble Under Influence:</strong> Avoid playing when impaired</li>
    <li><strong>Balance Your Life:</strong> Gaming should be one of many leisure activities</li>
</ul>

<h3>Warning Signs</h3>
<p>You may have a problem if you:</p>
<ul>
    <li>Spend more money than you can afford</li>
    <li>Chase losses by playing more</li>
    <li>Lie to family/friends about your gaming</li>
    <li>Feel anxious or irritable when not playing</li>
    <li>Neglect work, family, or personal responsibilities</li>
    <li>Borrow money to continue playing</li>
</ul>

<h3>Self-Exclusion</h3>
<p>If you feel you need a break, you can request self-exclusion for a period of your choice. Contact our support team to set this up.</p>

<h3>Get Help</h3>
<p>If you or someone you know needs help with problem gambling, contact:</p>
<ul>
    <li><strong>National Problem Gambling Helpline:</strong> 1800-XXX-XXXX</li>
    <li><strong>Gamblers Anonymous:</strong> www.gamblersanonymous.org</li>
</ul>

<h3>Age Verification</h3>
<p>Gaming is strictly for persons 18 years and older. We verify all accounts to prevent underage gaming.</p>

<h3>Contact Us</h3>
<p>For responsible gaming support, email: support@malamalweekly.com</p>
                ''',
                'meta_description': 'Learn about responsible gaming and player protection at Malamal Weekly',
                'footer_section': 'information',
                'order': 5
            },
        ]
        
        created_count = 0
        for page_data in pages_data:
            page, created = Page.objects.get_or_create(
                slug=page_data['slug'],
                defaults=page_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created page: {page.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Page already exists: {page.title}'))
        
        # Create Social Links
        social_links_data = [
            {'platform': 'facebook', 'url': 'https://facebook.com/malamalweekly', 'icon_class': 'bi bi-facebook', 'order': 1},
            {'platform': 'twitter', 'url': 'https://twitter.com/malamalweekly', 'icon_class': 'bi bi-twitter', 'order': 2},
            {'platform': 'instagram', 'url': 'https://instagram.com/malamalweekly', 'icon_class': 'bi bi-instagram', 'order': 3},
            {'platform': 'youtube', 'url': 'https://youtube.com/@malamalweekly', 'icon_class': 'bi bi-youtube', 'order': 4},
        ]
        
        social_created_count = 0
        for social_data in social_links_data:
            social, created = SocialLink.objects.get_or_create(
                platform=social_data['platform'],
                defaults=social_data
            )
            if created:
                social_created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created social link: {social.get_platform_display()}'))
            else:
                self.stdout.write(self.style.WARNING(f'Social link already exists: {social.get_platform_display()}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ CMS initialization complete!'))
        self.stdout.write(self.style.SUCCESS(f'  - {created_count} new pages created'))
        self.stdout.write(self.style.SUCCESS(f'  - {social_created_count} new social links created'))
