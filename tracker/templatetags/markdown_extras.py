import markdown
import bleach

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdown")
def markdown_filter(value):
    if not value:
        return ""

    html = markdown.markdown(
        value,
        extensions=[
            "extra",
            "nl2br",
            "sane_lists",
            "tables",
        ],
    )

    allowed_tags = [
        "p", "br",
        "strong", "em", "del",
        "h1", "h2", "h3", "h4", "h5", "h6",
        "ul", "ol", "li",
        "blockquote",
        "code", "pre",
        "table", "thead", "tbody", "tr", "th", "td",
        "a",
    ]

    allowed_attributes = {
        "a": ["href", "title", "target", "rel"],
    }

    html = bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=["http", "https", "mailto"],
    )

    return mark_safe(html)