import re
from django import template

register = template.Library()

@register.filter
def remove_media(html):
    if not html:
        return ""
    html = re.sub(r'<img[^>]*>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<video[^>]*>.*?</video>', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<table[^>]*>.*?</table>', '', html, flags=re.IGNORECASE | re.DOTALL)
    return html
