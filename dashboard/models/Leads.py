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
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=12)
    email = models.EmailField(max_length=255)
    linkedln = models.URLField(max_length=255, verbose_name="LinkedIn URL")
    facebook_id = models.URLField(max_length=255, verbose_name="Facebook URL")
    twitter = models.URLField(max_length=255, verbose_name="Twitter URL")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    reference = models.CharField(max_length=5000)
    type = models.CharField(max_length=10, choices=LEAD_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

