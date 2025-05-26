from celery import shared_task
import logging
from campaign.models.Campaign import Campaign
from dashboard.models import Lead
from email_handler.views import send_daily_message
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache

logger = logging.getLogger(__name__)


@shared_task(name='campaign.tasks.fetch_pending_campaigns')
def fetch_pending_campaigns(limit=None):
    """
    Fetches campaigns and sends emails based on:
    1. Campaign active period (started_at to ended_at)
    2. Daily time window (send_start_time to send_end_time)
    3. Hourly email limit (emails_per_hour)
    """
    try:
        now = timezone.now()
        current_time = now.time()

        # Start campaigns whose start time has passed
        campaigns_to_start = Campaign.objects.filter(
            status='pending',
            started_at__lte=now
        )

        if campaigns_to_start.exists():
            count = campaigns_to_start.update(status='active')
            logger.info(f"Started {count} campaigns based on their start time")

        # Get active campaigns within their active period
        active_campaigns = Campaign.objects.filter(
            status='active',
            started_at__lte=now,
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

        # Process each campaign
        total_emails_sent = 0
        campaigns_processed = []

        for campaign in active_campaigns:
            # Check if current time is within daily send window
            if not is_within_daily_send_window(campaign, current_time):
                logger.info(f"Campaign {campaign.id} '{campaign.name}' is outside daily send window "
                            f"({campaign.send_start_time} - {campaign.send_end_time})")
                continue

            # Track hourly email limit
            hourly_key = f"campaign_{campaign.id}_hourly_{now.strftime('%Y%m%d%H')}"
            hourly_count = cache.get(hourly_key, 0)

            if hourly_count >= campaign.emails_per_hour:
                logger.info(f"Campaign {campaign.id} '{campaign.name}' reached hourly limit "
                            f"({hourly_count}/{campaign.emails_per_hour})")
                continue

            # Track which leads have been sent emails
            sent_leads_key = f"campaign_{campaign.id}_sent_leads"
            sent_lead_ids = cache.get(sent_leads_key, set())

            # Get unsent leads
            unsent_leads = [
                lead for lead in leads if lead.id not in sent_lead_ids]

            if not unsent_leads:
                # All emails sent for this campaign
                campaign.status = 'complete'
                campaign.save()
                logger.info(
                    f"Campaign {campaign.id} '{campaign.name}' completed - all emails sent")
                continue

            # Calculate how many emails we can send this hour
            remaining_hourly_quota = campaign.emails_per_hour - hourly_count

            # Send emails up to the hourly limit
            emails_to_send = min(len(unsent_leads), remaining_hourly_quota)
            batch_sent_count = 0

            for i in range(emails_to_send):
                lead = unsent_leads[i]
                try:
                    send_daily_message(lead, campaign)
                    batch_sent_count += 1
                    sent_lead_ids.add(lead.id)
                    logger.debug(
                        f"Sent email for campaign {campaign.id} to lead {lead.id}")
                except Exception as e:
                    logger.error(
                        f"Error sending email for campaign {campaign.id} to lead {lead.id}: {str(e)}")

            # Update counters
            if batch_sent_count > 0:
                total_emails_sent += batch_sent_count
                hourly_count += batch_sent_count

                # Update cache
                cache.set(hourly_key, hourly_count, 3600)  # 1 hour expiry
                cache.set(sent_leads_key, sent_lead_ids,
                          86400 * 30)  # 30 days expiry

                campaigns_processed.append(campaign.id)
                logger.info(f"Campaign {campaign.id} '{campaign.name}': Sent {batch_sent_count} emails "
                            f"(hourly total: {hourly_count}/{campaign.emails_per_hour})")

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
            "campaigns_processed": len(campaigns_processed),
            "emails_sent": total_emails_sent
        }

    except Exception as e:
        logger.error(f"Error in fetch_pending_campaigns: {str(e)}")
        return {"status": "error", "message": str(e)}


def is_within_daily_send_window(campaign, current_time):
    """
    Check if current time is within the campaign's daily send window
    """
    start_time = campaign.send_start_time
    end_time = campaign.send_end_time

    if start_time <= end_time:
        # Normal case (e.g., 9 AM to 5 PM)
        return start_time <= current_time <= end_time
    else:
        # Overnight case (e.g., 10 PM to 2 AM)
        return current_time >= start_time or current_time <= end_time
