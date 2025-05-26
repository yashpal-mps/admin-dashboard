import json
from email_handler.views import send_daily_message
from campaign.models.Campaign import Campaign
from dashboard.models import Lead  # Import Lead model
from django.http import JsonResponse

# Create a Lead with minimal information
def create_minimal_lead(email):
    """
    Create a new Lead with the given email and default values for other fields.
    
    Parameters:
    - email: Email address for the lead
    
    Returns:
    - Lead object
    """
    lead = Lead(
        name="",
        company_name="",
        phone_no="",
        email=email,
        linkedln="",
        facebook_id="",
        twitter="",
        city="",
        state="",
        country="",
        reference="",
        type=""  
    )
    lead.save()
    return lead

# Updated SendEmail view
def SendEmail(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            campaign_id = data.get('campaign_id')
            email = data.get('email')
            
            if not email:
                return JsonResponse({'error': 'Email is required'}, status=400)
                
            # Get the campaign
            campaign = Campaign.objects.get(id=campaign_id)
            
            lead = create_minimal_lead(email)
            send_daily_message(lead, campaign)
            
            return JsonResponse({'message': 'Email sent successfully!'})
        except Campaign.DoesNotExist:
            return JsonResponse({'error': 'Campaign not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)