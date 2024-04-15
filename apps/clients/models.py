from django.db import models


# Create your models here.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Client(TimeStampedModel):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        Female = "female", "Female"

    class Country(models.TextChoices):
        PHILIPPINES = "philippines", "Philippines"

    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    birth = models.DateField(blank=False)
    gender = models.CharField(max_length=50, choices=Gender.choices)
    country = models.CharField(max_length=100, choices=Country.choices)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    contact_no = models.CharField(max_length=50)
    occupation = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="client_photos", null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def display_display_address(self):
        return (
            f"{self.address}, {self.city},  {self.state} {self.zip_code} {self.country}"
        )

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"
