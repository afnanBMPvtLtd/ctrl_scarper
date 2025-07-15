from django import forms

class ScrapeForm(forms.Form):
    url = forms.URLField(
        label='Website URL',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com'
        })
    )
