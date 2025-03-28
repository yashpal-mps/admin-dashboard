from django.contrib import admin
from campaign.models.Campaign import Campaign


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'agent', 'started_at',
                    'ended_at', 'created_at', 'updated_at')
    list_filter = ('agent', 'started_at', 'ended_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
