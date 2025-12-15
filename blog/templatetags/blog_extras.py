import re
from django import template

register = template.Library()

@register.filter
def remove_media(html):
    if not html:
        return ""
    # Remove img and video tags
    html = re.sub(r'<img[^>]*>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<video[^>]*>.*?</video>', '', html, flags=re.IGNORECASE | re.DOTALL)
    return html
