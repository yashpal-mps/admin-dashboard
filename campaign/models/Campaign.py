from django.db import models
from product.models.Product import Product
from agent.models.Agent import Agent
from dashboard.models.Leads import Lead


class Campaign(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('complete', 'Complete'),
        ('cancelled', 'Cancelled'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    products = models.ManyToManyField(Product, related_name="campaigns")
    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name="campaigns")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    leads = models.ManyToManyField(Lead, related_name="campaigns")
    # leads_member_name = models.ManyToManyField(Lead, related_name="campaigns_member_name")
    # leads_by_status = models.ManyToManyField(Lead, related_name="campaigns_by_status")
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_filtered_leads_for_campaign(self, status=None, company_name=None):
        # Get the leads related to this campaign
        leads = self.leads.all()

        # Apply filters if any
        if status:
            leads = leads.filter(type=status)  # Filter by status
        if company_name:
            leads = leads.filter(company_name__icontains=company_name)  # Filter by company name
        
        # Return the filtered queryset of leads
        return leads

    def get_leads_info(self):
        # Fetch the related leads with their status and company name
        lead_info = []
        for lead in self.leads.all():
            lead_info.append({
                'company_name': lead.company_name,
                'status': lead.get_type_display(),  # This will show the human-readable status
            })
        return lead_info