from django import forms
from apps.clients.models import Client


class DateInput(forms.DateInput):
    input_type = "date"


class ClientForm(forms.ModelForm):
    photo = forms.ImageField(widget=forms.FileInput)

    class Meta:
        model = Client
        fields = (
            "photo",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "birth",
            "gender",
            "country",
            "address",
            "city",
            "state",
            "zip_code",
            "contact_no",
            "occupation",
        )

        widgets = {
            "birth": DateInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # # Access choices for the 'gender' field
        # gender_choices = models.Client.Gender.choices
        country_choices = Client.Country.choices

        # Update the choices for the 'gender' field
        # self.fields['gender'].choices = gender_choices
        self.fields["country"].choices = country_choices
