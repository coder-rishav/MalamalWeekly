from .models import Page, SocialLink, SiteSettings


def cms_context(request):
    """Add CMS data to all templates"""
    return {
        'site_settings': SiteSettings.get_settings(),
        'footer_quick_links': Page.objects.filter(
            is_active=True, 
            show_in_footer=True, 
            footer_section='quick_links'
        ),
        'footer_information_pages': Page.objects.filter(
            is_active=True, 
            show_in_footer=True, 
            footer_section='information'
        ),
        'social_links': SocialLink.objects.filter(is_active=True),
    }
