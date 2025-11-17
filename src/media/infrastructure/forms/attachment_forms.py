"""
core attachment form.
"""

from django.utils.translation import gettext_lazy as _

from shared.infrastructure import forms


class UpsertAttachmentForm(forms.Form):
    is_ajax_form = True
    ajax_success_callbacK_method_name = "attachmentHasBeenManaged"
    ajax_error_callback_method_name = "attachmentManagerHasError"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        attachment_id = self.initial.get("attachment_id") or self.data.get("attachment_id")
        if attachment_id:
            self.fields["file"].required = False

    # attachment id
    attachment_id = forms.CharField(
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

    # attachment file
    file = forms.FileField(
        required=True,
        label=_("File"),
        help_text=_("File attachment"),
    )

    # title of the file
    title = forms.CharField(
        max_length=300,
        required=False,
        label=_("Title"),
        help_text=_("Title of the file"),
    )

