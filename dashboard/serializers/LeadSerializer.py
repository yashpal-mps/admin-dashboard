from rest_framework import serializers
from dashboard.models import Leads

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leads
        fields = '__all__'