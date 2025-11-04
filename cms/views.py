from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from .models import Page


def page_view(request, slug):
    """Display a CMS page"""
    page = get_object_or_404(Page, slug=slug, is_active=True)
    
    context = {
        'page': page,
    }
    return render(request, 'cms/page.html', context)


class PageDetailView(DetailView):
    """Class-based view for CMS pages"""
    model = Page
    template_name = 'cms/page.html'
    context_object_name = 'page'
    
    def get_queryset(self):
        return Page.objects.filter(is_active=True)
