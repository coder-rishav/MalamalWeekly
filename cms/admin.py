from django.contrib import admin
from .models import Page, SocialLink, SiteSettings


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'show_in_footer', 'footer_section', 'order', 'updated_at']
    list_filter = ['is_active', 'show_in_footer', 'footer_section']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'show_in_footer', 'order']
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['platform', 'url', 'is_active', 'order']
    list_filter = ['is_active', 'platform']
    list_editable = ['is_active', 'order']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Basic Info', {
            'fields': ('site_name', 'tagline', 'description')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'contact_address', 'support_hours')
        }),
        ('Footer', {
            'fields': ('footer_copyright', 'footer_tagline')
        }),
        ('SEO', {
            'fields': ('meta_keywords', 'google_analytics_id'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one settings object
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
