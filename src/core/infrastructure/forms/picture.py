"""
core picture form.
"""

import uuid
from django.utils.translation import gettext_lazy as _

from shared.infrastructure import forms


class UpsertPictureForm(forms.Form):
    # content type
    content_type = forms.CharField(
        required=True,
        max_length=1,
        widget=forms.HiddenInput(),
    )

    # object id (this id is generated at the first place)
    object_id = forms.CharField(
        required=True,
        widget=forms.HiddenInput(),
    )

    # picture
    image = forms.ImageField(
        required=False,
        help_text=_("Image file"),
    )
    # alternative text
    alternative = forms.CharField(
        max_length=300,
        required=False,
        help_text=_("Alternative text for image"),
    )
    # title of the image
    title = forms.CharField(
        max_length=300,
        required=False,
        help_text=_("Title of the image"),
    )
