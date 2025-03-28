from celery import shared_task
import logging
from campaign.models.Campaign import Campaign
from dashboard.models import Lead
from email_handler.views import send_daily_message

logger = logging.getLogger(__name__)


@shared_task(name='campaign.tasks.fetch_pending_campaigns')
def fetch_pending_campaigns(limit=None):
    """
    Fetches campaigns with 'pending' status and processes them by sending emails to leads

    Args:
        limit (int, optional): Maximum number of campaigns to process
    """
    try:
        # Get pending campaigns
        pending_campaigns = Campaign.objects.filter(status='pending')

        if limit:
            pending_campaigns = pending_campaigns[:limit]

        campaign_count = pending_campaigns.count()
        logger.info(f"Found {campaign_count} pending campaigns")

        if campaign_count == 0:
            return {"status": "success", "message": "No pending campaigns found."}

        # Get all leads
        leads = Lead.objects.all()
        lead_count = leads.count()

        if lead_count == 0:
            logger.warning("No leads found in the database.")
            return {"status": "warning", "message": "No leads found to send emails to."}

        # Process each campaign for each lead
        email_sent_count = 0
        for campaign in pending_campaigns:
            for lead in leads:
                try:
                    send_daily_message(lead, campaign)
                    email_sent_count += 1
                except Exception as e:
                    logger.error(
                        f"Error sending email for campaign {campaign.id} to lead {lead.id}: {str(e)}")

        logger.info(
            f"Processed {campaign_count} campaigns, sent {email_sent_count} emails")

        return {
            "status": "success",
            "campaigns_processed": campaign_count,
            "emails_sent": email_sent_count
        }

    except Exception as e:
        logger.error(f"Error in fetch_pending_campaigns: {str(e)}")
        return {"status": "error", "message": str(e)}
