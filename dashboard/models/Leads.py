from django.db import models

# Create your models here.


class Lead(models.Model):
    # Lead Status Choices
    LEAD_STATUS = (
        ("won", "Won"),
        ("hot", "Hot"),
        ("warm", "Warm"),
        ("cold", "Cold"),
        ("lost", "Lost")
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    phone_no = models.CharField(max_length=12, null=True, blank=True)
    email = models.EmailField(max_length=255)
    linkedln = models.URLField(
        max_length=255, verbose_name="LinkedIn URL", null=True, blank=True)
    facebook_id = models.URLField(
        max_length=255, verbose_name="Facebook URL", null=True, blank=True)
    twitter = models.URLField(
        max_length=255, verbose_name="Twitter URL", null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    reference = models.CharField(max_length=5000, null=True, blank=True)
    type = models.CharField(
        max_length=10, choices=LEAD_STATUS, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.email
