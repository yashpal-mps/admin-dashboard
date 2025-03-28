from django.contrib import admin
from campaign.models.Campaign import Campaign
from dashboard.models.Leads import Lead

class CampaignAdmin(admin.ModelAdmin):
    # Display fields for the Campaign Admin
    list_display = ['name', 'status', 'started_at', 'ended_at', 'get_leads_info_display']
    list_filter = ['status']  # Filter by campaign status
    filter_horizontal = ['leads']  # Horizontal filter for many-to-many leads

    # Custom method to display leads with their statuses
    def get_leads_info_display(self, obj):
        # Fetching the leads info from the Campaign model's custom method
        lead_info = obj.get_leads_info()
        return ", ".join([f"{info['company_name']} ({info['status']})" for info in lead_info])

    # Add a short description for clarity in the admin interface
    get_leads_info_display.short_description = 'Leads Info'

# Register the customized Campaign Admin
admin.site.register(Campaign, CampaignAdmin)