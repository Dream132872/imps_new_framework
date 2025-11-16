"""
core picture form.
"""

from django.utils.translation import gettext_lazy as _

from shared.infrastructure import forms


class UpsertPictureForm(forms.Form):
    is_ajax_form = True
    ajax_success_callbacK_method_name = "pictureHasBeenManaged"
    ajax_error_callback_method_name = "pictureManagerHasError"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        picture_id = self.initial.get("picture_id") or self.data.get("picture_id")
        if picture_id:
            self.fields["image"].required = False

    # picture id
    picture_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.HiddenInput(),
    )

    # content type
    content_type = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput(),
    )

    # object id (this id is generated at the first place)
    object_id = forms.CharField(
        required=True,
        widget=forms.HiddenInput(),
    )

    # picture type system name ( like main, avatar, etc ...)
    picture_type = forms.CharField(
        required=True,
        widget=forms.HiddenInput(),
    )

    # picture
    image = forms.ImageField(
        required=True,
        label=_("Image file"),
        help_text=_("Image file"),
    )

    # title of the image
    title = forms.CharField(
        max_length=300,
        required=False,
        label=_("Title"),
        help_text=_("Title of the image"),
    )

    # alternative text
    alternative = forms.CharField(
        max_length=300,
        required=False,
        label=_("Alternative"),
        help_text=_("Alternative text for image"),
    )

