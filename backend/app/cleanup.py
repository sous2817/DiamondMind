"""
Cleanup module for removing orphaned swing records.

This module provides scheduled cleanup of:
- Swings stuck in 'processing' or 'pending' state for > 24 hours
- Swings in 'failed' state for > 7 days
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Swing, SwingStatus
import logging

logger = logging.getLogger("cleanup")


def cleanup_orphaned_swings():
    """
    Remove orphaned swing records based on status and age.
    
    Cleanup rules:
    - Delete swings with status='processing' or 'pending' older than 24 hours
    - Delete swings with status='failed' older than 7 days
    - Never delete swings with status='completed'
    """
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # Threshold for processing/pending swings: 24 hours
        processing_threshold = now - timedelta(hours=24)
        
        # Threshold for failed swings: 7 days
        failed_threshold = now - timedelta(days=7)
        
        # Find orphaned processing/pending swings
        orphaned_processing = db.query(Swing).filter(
            Swing.status.in_([SwingStatus.PROCESSING, SwingStatus.PENDING]),
            Swing.created_at < processing_threshold
        ).all()
        
        # Find old failed swings
        old_failed = db.query(Swing).filter(
            Swing.status == SwingStatus.FAILED,
            Swing.created_at < failed_threshold
        ).all()
        
        # Delete orphaned swings
        deleted_count = 0
        for swing in orphaned_processing:
            logger.info(f"Deleting orphaned swing {swing.id} (status={swing.status.value}, age={(now - swing.created_at).total_seconds() / 3600:.1f}h)")
            db.delete(swing)
            deleted_count += 1
        
        for swing in old_failed:
            logger.info(f"Deleting old failed swing {swing.id} (age={(now - swing.created_at).days} days)")
            db.delete(swing)
            deleted_count += 1
        
        if deleted_count > 0:
            db.commit()
            logger.info(f"✅ Cleanup complete: Deleted {deleted_count} orphaned swings")
        else:
            logger.info("✅ Cleanup complete: No orphaned swings found")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
