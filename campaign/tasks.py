from celery import shared_task
import logging
from campaign.models.Campaign import Campaign
from dashboard.models import Lead
from email_handler.views import send_daily_message
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name='campaign.tasks.fetch_pending_campaigns')
def fetch_pending_campaigns(limit=None):
    """
    Fetches campaigns with 'pending' status whose start time has passed,
    processes them by sending emails to leads, and updates status to 'complete'
    when the end time has passed or all tasks are completed.

    Args:
        limit (int, optional): Maximum number of campaigns to process
    """
    try:
        now = timezone.now()

        # Start campaigns whose start time has passed but are still in pending status
        campaigns_to_start = Campaign.objects.filter(
            status='pending',
            started_at__lte=now
        )

        if campaigns_to_start.exists():
            count = campaigns_to_start.update(status='active')
            logger.info(f"Started {count} campaigns based on their start time")

        # Get active campaigns that haven't reached their end time
        active_campaigns = Campaign.objects.filter(
            status='active',
            ended_at__gt=now
        )

        if limit:
            active_campaigns = active_campaigns[:limit]

        campaign_count = active_campaigns.count()
        logger.info(f"Found {campaign_count} active campaigns to process")

        if campaign_count == 0:
            # End campaigns that have passed their end time
            ended_campaigns = Campaign.objects.filter(
                status='active',
                ended_at__lte=now
            )
            if ended_campaigns.exists():
                count = ended_campaigns.update(status='complete')
                logger.info(
                    f"Completed {count} campaigns based on their end time")

            return {"status": "success", "message": "No active campaigns to process."}

        # Get all leads
        leads = Lead.objects.all()
        lead_count = leads.count()

        if lead_count == 0:
            logger.warning("No leads found in the database.")
            return {"status": "warning", "message": "No leads found to send emails to."}

        # Process each campaign for each lead
        email_sent_count = 0
        completed_campaigns = []

        for campaign in active_campaigns:
            campaign_email_count = 0
            campaign_success = True

            for lead in leads:
                try:
                    send_daily_message(lead, campaign)
                    email_sent_count += 1
                    campaign_email_count += 1
                except Exception as e:
                    campaign_success = False
                    logger.error(
                        f"Error sending email for campaign {campaign.id} to lead {lead.id}: {str(e)}")

            # If all emails were sent successfully for this campaign
            if campaign_success and campaign_email_count == lead_count:
                completed_campaigns.append(campaign.id)
                logger.info(
                    f"Campaign {campaign.id} completed successfully - all emails sent")

        # Update campaigns that have sent all emails to 'complete'
        if completed_campaigns:
            Campaign.objects.filter(
                id__in=completed_campaigns).update(status='complete')
            logger.info(
                f"Completed {len(completed_campaigns)} campaigns based on all emails being sent")

        logger.info(
            f"Processed {campaign_count} campaigns, sent {email_sent_count} emails")

        # End campaigns that have passed their end time
        ended_campaigns = Campaign.objects.filter(
            status='active',
            ended_at__lte=now
        )
        if ended_campaigns.exists():
            count = ended_campaigns.update(status='complete')
            logger.info(f"Completed {count} campaigns based on their end time")

        return {
            "status": "success",
            "campaigns_processed": campaign_count,
            "emails_sent": email_sent_count,
            "campaigns_completed_by_task": len(completed_campaigns)
        }

    except Exception as e:
        logger.error(f"Error in fetch_pending_campaigns: {str(e)}")
        return {"status": "error", "message": str(e)}
