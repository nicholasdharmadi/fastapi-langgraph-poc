"""Campaign processing tasks for RQ."""
import logging
from redis import Redis
from rq import Queue
from app.config import settings
from app.database import SessionLocal
from app.orchestrator.graph import process_campaign_lead_with_graph

logger = logging.getLogger(__name__)

# Initialize Redis connection
redis_conn = Redis.from_url(settings.REDIS_URL)
campaign_queue = Queue('campaigns', connection=redis_conn)


def process_campaign_task(campaign_id: int):
    """
    Process all pending leads in a campaign.
    
    Args:
        campaign_id: ID of the campaign to process
    """
    from app.models import Campaign, CampaignLead
    from app.models.campaign import CampaignStatus
    from datetime import datetime
    
    db = SessionLocal()
    
    try:
        logger.info(f"Starting campaign processing: {campaign_id}")
        
        # Get campaign
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return
        
        # Update campaign status
        campaign.status = CampaignStatus.PROCESSING
        campaign.started_at = datetime.now()
        db.commit()
        
        # Get all pending campaign leads
        pending_leads = db.query(CampaignLead).filter(
            CampaignLead.campaign_id == campaign_id,
            CampaignLead.status == 'pending'
        ).all()
        
        logger.info(f"Found {len(pending_leads)} pending leads to process")
        
        # Process each lead sequentially (can be parallelized later)
        for campaign_lead in pending_leads:
            # Check if campaign was paused
            db.refresh(campaign)
            if campaign.status == CampaignStatus.PAUSED:
                logger.info(f"Campaign {campaign_id} paused. Stopping processing.")
                return

            try:
                result = process_campaign_lead_with_graph(campaign_lead.id, db)
                logger.info(f"Processed lead {campaign_lead.id}: {result['status']}")
            except Exception as e:
                logger.error(f"Error processing lead {campaign_lead.id}: {str(e)}")
        
        # Update campaign status
        campaign.status = CampaignStatus.COMPLETED
        campaign.completed_at = datetime.now()
        campaign.update_stats()
        db.commit()
        
        logger.info(f"Campaign {campaign_id} processing complete")
        
    except Exception as e:
        logger.error(f"Error in campaign task: {str(e)}")
        
        # Update campaign status to failed
        try:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if campaign:
                campaign.status = CampaignStatus.FAILED
                db.commit()
        except Exception as update_error:
            logger.error(f"Error updating campaign status: {str(update_error)}")
    
    finally:
        db.close()


def enqueue_campaign_processing(campaign_id: int) -> str:
    """
    Enqueue a campaign for processing.
    
    Args:
        campaign_id: ID of the campaign to process
    
    Returns:
        Job ID
    """
    job = campaign_queue.enqueue(
        process_campaign_task,
        campaign_id,
        job_timeout='1h'
    )
    logger.info(f"Enqueued campaign {campaign_id} processing: job {job.id}")
    return job.id

