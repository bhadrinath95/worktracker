import bleach
import markdown

from bleach.css_sanitizer import CSSSanitizer


ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS).union({
    "p", "h1", "h2", "h3", "h4", "hr", "br",
    "img", "video", "source", "pre", "code",
    "table", "thead", "tbody", "tr", "th", "td",
    "del", "sup", "sub",
})

ALLOWED_ATTRIBUTES = {
    "*": ["class"],
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height", "style", "loading"],
    "video": ["controls", "width", "height", "poster", "style", "preload"],
    "source": ["src", "type"],
    "th": ["align"],
    "td": ["align"],
}

CSS_SANITIZER = CSSSanitizer(allowed_css_properties=[
    "width", "max-width", "height", "max-height", "object-fit",
    "border-radius", "border", "display", "margin", "margin-left",
    "margin-right",
])

def render_story_markdown(source):
    """Convert Markdown + permitted inline media HTML into safe HTML."""
    rendered = markdown.markdown(
        source or "",
        extensions=["extra", "sane_lists", "fenced_code", "nl2br"],
        output_format="html5",
    )
    return bleach.clean(
        rendered,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols={"http", "https", "mailto"},
        css_sanitizer=CSS_SANITIZER,
        strip=True,
    )
