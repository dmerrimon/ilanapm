"""
Scheduled Tasks for ML Model Maintenance

Handles periodic model performance checks and retraining
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


def setup_scheduled_tasks() -> BackgroundScheduler:
    """
    Setup and start scheduled tasks for ML model maintenance

    Returns:
        BackgroundScheduler: Started scheduler instance
    """
    scheduler = BackgroundScheduler()

    # Check model performance weekly (every Sunday at 2 AM)
    scheduler.add_job(
        check_model_performance_job,
        trigger=CronTrigger(day_of_week='sun', hour=2, minute=0),
        id='performance_check',
        name='Weekly Model Performance Check',
        misfire_grace_time=3600  # Allow 1 hour grace period if missed
    )
    logger.info("Scheduled: Weekly model performance check (Sundays at 2:00 AM)")

    # Retrain model monthly (first day of month at 3 AM)
    scheduler.add_job(
        retrain_model_job,
        trigger=CronTrigger(day=1, hour=3, minute=0),
        id='model_retraining',
        name='Monthly Model Retraining',
        misfire_grace_time=7200  # Allow 2 hour grace period if missed
    )
    logger.info("Scheduled: Monthly model retraining (1st of month at 3:00 AM)")

    # Start scheduler
    scheduler.start()
    logger.info("✓ Scheduled tasks started successfully")

    return scheduler


def check_model_performance_job():
    """
    Scheduled job to check model performance and log recommendations
    """
    try:
        logger.info("=" * 80)
        logger.info("Starting scheduled model performance check...")
        logger.info("=" * 80)

        from ml_advisory.accuracy_monitor import check_model_performance

        result = check_model_performance()

        if result['needs_retraining']:
            logger.warning(
                f"⚠️  Model retraining recommended based on performance metrics"
            )
            for reason in result['reasons']:
                logger.warning(f"  - {reason}")

            # Log summary
            report = result.get('report', {})
            logger.warning(
                f"Current accuracy: {report.get('accuracy_rate', 0):.1%} "
                f"({report.get('total_predictions', 0)} predictions)"
            )
        else:
            report = result.get('report', {})
            logger.info(
                f"✓ Model performance acceptable: {report.get('accuracy_rate', 0):.1%} "
                f"({report.get('total_predictions', 0)} predictions)"
            )

        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error in scheduled performance check: {e}")


def retrain_model_job():
    """
    Scheduled job to retrain ML models using feedback data
    """
    try:
        logger.info("=" * 80)
        logger.info("Starting scheduled model retraining...")
        logger.info("=" * 80)

        from ml_advisory.retrain_models import retrain_duration_model

        success = retrain_duration_model()

        if success:
            logger.info("✓ Scheduled model retraining completed successfully")
        else:
            logger.warning("⚠️  Scheduled model retraining failed or skipped (insufficient data)")

        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error in scheduled retraining: {e}")


def get_scheduler_status() -> dict:
    """
    Get status of scheduled tasks (for monitoring)

    Returns:
        dict: Scheduler status information
    """
    # This would be implemented to return scheduler status
    # For now, return basic info
    return {
        'enabled': True,
        'jobs': [
            {
                'id': 'performance_check',
                'name': 'Weekly Model Performance Check',
                'schedule': 'Sundays at 2:00 AM UTC'
            },
            {
                'id': 'model_retraining',
                'name': 'Monthly Model Retraining',
                'schedule': '1st of month at 3:00 AM UTC'
            }
        ]
    }


if __name__ == "__main__":
    # For testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Testing scheduled tasks setup...")
    scheduler = setup_scheduled_tasks()
    print("\nScheduled jobs:")
    for job in scheduler.get_jobs():
        print(f"  - {job.name}: {job.trigger}")

    # Keep running for a few seconds to show it works
    import time
    print("\nScheduler running (press Ctrl+C to stop)...")
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        print("\nShutting down scheduler...")
        scheduler.shutdown()
        print("Done.")
