from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Page(models.Model):
    """Dynamic CMS Pages"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly version of title")
    content = models.TextField(help_text="Page content (HTML supported)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    is_active = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=True, help_text="Display link in footer")
    footer_section = models.CharField(max_length=50, choices=[
        ('quick_links', 'Quick Links'),
        ('information', 'Information'),
        ('none', 'None')
    ], default='information')
    order = models.IntegerField(default=0, help_text="Display order in footer")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_pages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class SocialLink(models.Model):
    """Social Media Links"""
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('linkedin', 'LinkedIn'),
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, unique=True)
    url = models.URLField()
    icon_class = models.CharField(max_length=50, default='bi bi-link', help_text="Bootstrap icon class")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'platform']
        
    def __str__(self):
        return f"{self.get_platform_display()} - {self.url}"
    
    def get_default_icon(self):
        """Get default Bootstrap icon for platform"""
        icons = {
            'facebook': 'bi bi-facebook',
            'twitter': 'bi bi-twitter',
            'instagram': 'bi bi-instagram',
            'youtube': 'bi bi-youtube',
            'linkedin': 'bi bi-linkedin',
            'telegram': 'bi bi-telegram',
            'whatsapp': 'bi bi-whatsapp',
        }
        return icons.get(self.platform, 'bi bi-link')


class SiteSettings(models.Model):
    """Global Site Settings"""
    site_name = models.CharField(max_length=200, default='Malamal Weekly')
    tagline = models.CharField(max_length=300, default='Your trusted online lottery and gaming platform.')
    description = models.TextField(default='Experience the thrill of winning with secure, fair, and exciting games.')
    contact_email = models.EmailField(default='support@malamalweekly.com')
    contact_phone = models.CharField(max_length=20, default='+91 1234567890')
    contact_address = models.CharField(max_length=200, default='Mumbai, India')
    support_hours = models.CharField(max_length=100, default='24/7 Support')
    footer_copyright = models.CharField(max_length=200, default='© 2025 Malamal Weekly. All rights reserved.')
    footer_tagline = models.CharField(max_length=200, default='Secure & Licensed Platform')
    
    # SEO
    meta_keywords = models.CharField(max_length=300, blank=True)
    google_analytics_id = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name
    
    @classmethod
    def get_settings(cls):
        """Get or create site settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
