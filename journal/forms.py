class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = [
            "topic",
            "order_no",
            "heading",
            "description",
            "desktop_background_url",
            "mobile_background_url",
            "story_datetime",
        ]
        widgets = {
            "topic": forms.Select(attrs={"class": "form-select"}),

            "order_no": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter order number",
                "min": 1,
            }),

            "heading": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter story heading",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control journal-markdown-input",
                "rows": 18,
                "placeholder": "Write your story in Markdown. You can add HTML img and video tags inline.",
                "spellcheck": "true",
            }),

            "desktop_background_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://raw.githubusercontent.com/tenctech10c/Images/main/{image}.{ext}",
            }),

            "mobile_background_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://raw.githubusercontent.com/tenctech10c/Images/main/{image}.{ext}",
            }),

            "story_datetime": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["story_datetime"].input_formats = ["%Y-%m-%dT%H:%M"]

        self.fields["desktop_background_url"].initial = (
            "https://raw.githubusercontent.com/tenctech10c/Images/main/{image}.{ext}"
        )

        self.fields["mobile_background_url"].initial = (
            "https://raw.githubusercontent.com/tenctech10c/Images/main/{image}.{ext}"
        )