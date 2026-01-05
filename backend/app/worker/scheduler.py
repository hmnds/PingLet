"""Scheduler for background jobs."""
from datetime import datetime, time, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import structlog
from app.config import settings
from app.database import SessionLocal, engine
from app.services.ingestion import IngestionService
from app.services.x_client import RealXClient
from app.services.alerts import AlertEngine
from app.services.embeddings import EmbeddingsService
from app.services.llm import LLMService
from app.services.digest import DigestService
from app.notifiers.log import LogNotifier
from app.models import Post

logger = structlog.get_logger()


def run_ingestion_job():
    """Job to run ingestion for all accounts."""
    logger.info("Starting ingestion job")
    db = SessionLocal()
    try:
        x_client = RealXClient()
        service = IngestionService(x_client, db)
        result = service.ingest_all_accounts()
        
        logger.info(
            "Ingestion job completed",
            accounts_processed=result["accounts_processed"],
            posts_fetched=result["posts_fetched"],
            posts_stored=result["posts_stored"],
            errors_count=len(result["errors"]),
        )
        
        # Check new posts for alerts
        if result["posts_stored"] > 0:
            check_alerts_for_new_posts(db)
    except Exception as e:
        logger.error("Ingestion job failed", error=str(e))
    finally:
        db.close()


def check_alerts_for_new_posts(db):
    """Check alerts for recently stored posts."""
    try:
        # Get posts from last 5 minutes (newly ingested)
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        new_posts = db.query(Post).filter(Post.stored_at >= cutoff).all()
        
        if not new_posts:
            return
        
        embeddings_service = EmbeddingsService()
        llm_service = LLMService()
        notifier = LogNotifier()
        alert_engine = AlertEngine(db, embeddings_service, llm_service, notifier)
        
        for post in new_posts:
            try:
                alert_engine.check_post(post)
            except Exception as e:
                logger.error("Failed to check alerts for post", post_id=post.id, error=str(e))
    except Exception as e:
        logger.error("Failed to check alerts", error=str(e))


def run_digest_job():
    """Job to generate daily digest."""
    logger.info("Starting digest job")
    db = SessionLocal()
    try:
        llm_service = LLMService()
        notifier = LogNotifier()
        service = DigestService(db, llm_service, notifier)
        digest = service.generate_digest()
        
        logger.info("Digest job completed", digest_id=digest.id, digest_date=digest.digest_date)
    except Exception as e:
        logger.error("Digest job failed", error=str(e))
    finally:
        db.close()


def start_scheduler():
    """Start the scheduler with configured jobs."""
    scheduler = BlockingScheduler()
    
    # Polling job: run every N minutes
    polling_interval = settings.polling_interval_minutes
    scheduler.add_job(
        run_ingestion_job,
        trigger=IntervalTrigger(minutes=polling_interval),
        id="ingestion_job",
        name="Ingestion Job",
        replace_existing=True,
    )
    logger.info("Scheduled ingestion job", interval_minutes=polling_interval)
    
    # Digest job: run at configured time
    digest_time_parts = settings.digest_time.split(":")
    hour = int(digest_time_parts[0])
    minute = int(digest_time_parts[1]) if len(digest_time_parts) > 1 else 0
    
    scheduler.add_job(
        run_digest_job,
        trigger=CronTrigger(hour=hour, minute=minute, timezone=settings.timezone),
        id="digest_job",
        name="Daily Digest Job",
        replace_existing=True,
    )
    logger.info("Scheduled digest job", time=settings.digest_time, timezone=settings.timezone)
    
    logger.info("Scheduler started")
    scheduler.start()


if __name__ == "__main__":
    start_scheduler()

