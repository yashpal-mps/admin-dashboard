from rest_framework import serializers
from campaign.models.Campaign import Campaign

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'