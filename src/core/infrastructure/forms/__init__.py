"""
Comprehensive test form for all custom widgets.
This form demonstrates all available widget types in the shared domain.
"""

from shared.infrastructure.forms import *
from parsley.decorators import parsleyfy
from django.utils.translation import gettext_lazy as _

from shared.infrastructure.forms.fields import PictureField


@parsleyfy
class TestWidgetsForm(Form):
    """
    Comprehensive test form showcasing all available custom widgets.
    This form can be used to test the rendering and functionality of all widgets.
    """

    class Meta:
        parsley_extras = {
            "email_input": {
                "equalto": "text_input",
                "equalto-message": _("This value should be equal to text_input"),
            }
        }

    form_title = "Custom Widgets Test Form"
    form_id = "test_form"

    picture = PictureField()

    # checkbox_input = BooleanField()

    # # Basic Input Widgets
    # text_input = CharField(
    #     label="Text Input",
    #     help_text="Basic text input field",
    #     placeholder="Enter some text",
    #     required=True,
    # )

    # email_input = EmailField(
    #     label="Email Input",
    #     help_text="Email input with validation",
    #     placeholder="Enter your email",
    #     required=True,
    # )

    # url_input = URLField(
    #     label="URL Input",
    #     help_text="URL input with validation",
    #     placeholder="Enter a URL",
    #     required=False,
    # )

    # number_input = IntegerField(
    #     label="Number Input",
    #     help_text="Numeric input field",
    #     placeholder="Enter a number",
    #     required=False,
    # )

    # decimal_input = DecimalField(
    #     label="Decimal Input",
    #     help_text="Decimal number input",
    #     placeholder="Enter a decimal number",
    #     required=False,
    # )

    # float_input = FloatField(
    #     label="Float Input",
    #     help_text="Floating point number input",
    #     placeholder="Enter a float number",
    #     required=False,
    # )

    # color_input = CharField(
    #     label="Color Input",
    #     help_text="Color picker input",
    #     widget=ColorInput(),
    #     required=False,
    # )

    # search_input = CharField(
    #     label="Search Input",
    #     help_text="Search input field",
    #     widget=SearchInput(),
    #     placeholder="Search for something",
    #     required=False,
    # )

    # tel_input = CharField(
    #     label="Telephone Input",
    #     help_text="Telephone number input",
    #     widget=TelInput(),
    #     placeholder="Enter phone number",
    #     required=False,
    # )

    # password_input = CharField(
    #     label="Password Input",
    #     help_text="Password input field",
    #     widget=PasswordInput(),
    #     placeholder="Enter password",
    #     required=False,
    # )

    # # Hidden Inputs
    # hidden_input = CharField(
    #     label="Hidden Input",
    #     widget=HiddenInput(),
    #     initial="hidden_value",
    #     required=False,
    # )

    # # File Inputs
    # file_input = FileField(
    #     label="File Input", help_text="Upload a file", required=False
    # )

    # clearable_file_input = FileField(
    #     label="Clearable File Input",
    #     help_text="Upload a file with clear option",
    #     widget=ClearableFileInput(),
    #     required=False,
    # )

    # # Text Areas
    # textarea_input = CharField(
    #     label="Textarea Input",
    #     help_text="Multi-line text input",
    #     widget=Textarea(),
    #     placeholder="Enter multiple lines of text",
    #     required=False,
    # )

    # rich_text_input = CharField(
    #     label="Rich Text Input",
    #     help_text="Rich text editor",
    #     widget=RichText(),
    #     required=False,
    # )

    # # Date/Time Inputs
    # date_input = DateField(
    #     label="Date Input", help_text="Date picker input", required=False
    # )

    # datetime_input = DateTimeField(
    #     label="DateTime Input", help_text="Date and time input", required=False
    # )

    # time_input = TimeField(
    #     label="Time Input", help_text="Time picker input", required=False
    # )

    # # Boolean Inputs
    # checkbox_input = BooleanField(
    #     label="Checkbox Input", help_text="Single checkbox", required=False
    # )

    # # Selection Widgets
    # select_input = ChoiceField(
    #     label="Select Input",
    #     help_text="Dropdown selection",
    #     choices=[
    #         ("", "Choose an option"),
    #         ("option1", "Option 1"),
    #         ("option2", "Option 2"),
    #         ("option3", "Option 3"),
    #     ],
    #     required=False,
    # )

    # null_boolean_select = forms.NullBooleanField(
    #     label="Null Boolean Select",
    #     help_text="Boolean with null option",
    #     widget=NullBooleanSelect(),
    #     required=False,
    # )

    # select_multiple_input = MultipleChoiceField(
    #     label="Select Multiple Input",
    #     help_text="Multiple selection dropdown",
    #     choices=[
    #         ("choice1", "Choice 1"),
    #         ("choice2", "Choice 2"),
    #         ("choice3", "Choice 3"),
    #         ("choice4", "Choice 4"),
    #     ],
    #     required=False,
    # )

    # radio_select_input = ChoiceField(
    #     label="Radio Select Input",
    #     help_text="Radio button selection",
    #     widget=RadioSelect(),
    #     choices=[
    #         ("radio1", "Radio Option 1"),
    #         ("radio2", "Radio Option 2"),
    #         ("radio3", "Radio Option 3"),
    #     ],
    #     required=False,
    # )

    # checkbox_select_multiple_input = MultipleChoiceField(
    #     label="Checkbox Select Multiple",
    #     help_text="Multiple checkbox selection",
    #     widget=CheckboxSelectMultiple(),
    #     choices=[
    #         ("check1", "Checkbox 1"),
    #         ("check2", "Checkbox 2"),
    #         ("check3", "Checkbox 3"),
    #         ("check4", "Checkbox 4"),
    #     ],
    #     required=False,
    # )

    # # Advanced Widgets
    # split_datetime_input = DateTimeField(
    #     label="Split DateTime Input",
    #     help_text="Separate date and time inputs",
    #     widget=SplitDateTimeWidget(),
    #     required=False,
    # )

    # split_hidden_datetime_input = DateTimeField(
    #     label="Split Hidden DateTime Input",
    #     help_text="Hidden split date and time inputs",
    #     widget=SplitHiddenDateTimeWidget(),
    #     required=False,
    # )

    # select_date_input = DateField(
    #     label="Select Date Input",
    #     help_text="Year/Month/Day selectors",
    #     widget=SelectDateWidget(),
    #     required=False,
    # )

    # # Multi-widget example
    # multi_widget_input = CharField(
    #     label="Multi Widget Input",
    #     help_text="Example of multi-widget",
    #     widget=MultiWidget([TextInput(), TextInput()]),
    #     required=False,
    # )
