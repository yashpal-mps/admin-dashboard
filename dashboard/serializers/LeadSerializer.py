from rest_framework import serializers
from dashboard.models.Leads import Lead

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'