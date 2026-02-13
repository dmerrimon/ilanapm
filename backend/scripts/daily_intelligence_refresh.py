"""
Daily Intelligence Refresh Job

Comprehensive background job that refreshes all intelligence data:
1. Study health snapshots (all projects)
2. Portfolio health metrics
3. Cross-study patterns
4. Systemic issues
5. Dashboard cache cleanup

Schedule:
    Run daily at midnight via cron:
    0 0 * * * cd /path/to/backend && python3 scripts/daily_intelligence_refresh.py

This ensures all dashboards have fresh data each morning.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(backend_dir / 'logs' / 'daily_intelligence_refresh.log')
    ]
)

logger = logging.getLogger(__name__)


def get_db_connection() -> sqlite3.Connection:
    """Get database connection"""
    db_path = backend_dir / "database" / "feedback.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def refresh_study_health_snapshots(conn: sqlite3.Connection) -> dict:
    """
    Refresh health snapshots for all projects

    Returns:
        Stats dict with counts
    """
    logger.info("Starting study health snapshot refresh")

    try:
        from intelligence.dashboard_service import refresh_all_health_snapshots

        refresh_all_health_snapshots(conn)

        # Count refreshed projects
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT project_id) as count
            FROM study_health_snapshots
            WHERE snapshot_date = date('now')
        """)

        count = cursor.fetchone()['count']

        logger.info(f"Refreshed {count} study health snapshots")

        return {"success": True, "studies_refreshed": count}

    except Exception as e:
        logger.error(f"Failed to refresh study health snapshots: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def refresh_portfolio_intelligence(conn: sqlite3.Connection) -> dict:
    """
    Refresh portfolio intelligence for all orgs

    Returns:
        Stats dict with counts
    """
    logger.info("Starting portfolio intelligence refresh")

    try:
        from intelligence.portfolio_service import PortfolioService, store_cross_study_patterns, store_systemic_issues
        import uuid
        import json

        cursor = conn.cursor()

        # Get all orgs with active projects
        cursor.execute("""
            SELECT DISTINCT org_id
            FROM signals
        """)

        orgs = [row['org_id'] for row in cursor.fetchall()]

        total_patterns = 0
        total_issues = 0

        for org_id in orgs:
            service = PortfolioService(conn)

            # Calculate portfolio health
            portfolio_health = service.get_portfolio_health(org_id)

            # Store portfolio health snapshot
            cursor.execute("""
                INSERT OR REPLACE INTO portfolio_health_snapshots (
                    snapshot_id, org_id, total_studies,
                    average_health_score, median_health_score,
                    healthy_count, warning_count, critical_count,
                    improving_count, declining_count, stable_count,
                    total_escalations, director_escalations, vp_escalations,
                    total_active_signals, total_high_priority_risks,
                    estimated_total_delay_days, estimated_total_cost_impact,
                    studies_needing_immediate_attention, studies_at_risk,
                    snapshot_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))
            """, (
                str(uuid.uuid4()),
                org_id,
                portfolio_health.total_studies,
                portfolio_health.average_health_score,
                portfolio_health.median_health_score,
                portfolio_health.healthy_count,
                portfolio_health.warning_count,
                portfolio_health.critical_count,
                portfolio_health.improving_count,
                portfolio_health.declining_count,
                portfolio_health.stable_count,
                portfolio_health.total_escalations,
                portfolio_health.director_escalations,
                portfolio_health.vp_escalations,
                portfolio_health.total_active_signals,
                portfolio_health.total_high_priority_risks,
                portfolio_health.estimated_total_delay_days,
                portfolio_health.estimated_total_cost_impact,
                json.dumps(portfolio_health.studies_needing_immediate_attention),
                json.dumps(portfolio_health.studies_at_risk)
            ))

            # Detect and store cross-study patterns
            patterns = service.detect_cross_study_patterns(org_id)
            store_cross_study_patterns(conn, patterns, org_id)
            total_patterns += len(patterns)

            # Detect and store systemic issues
            issues = service.detect_systemic_issues(org_id)
            store_systemic_issues(conn, issues, org_id)
            total_issues += len(issues)

            logger.info(
                f"Refreshed portfolio intelligence for org {org_id}: "
                f"{len(patterns)} patterns, {len(issues)} issues"
            )

        conn.commit()

        logger.info(
            f"Refreshed portfolio intelligence for {len(orgs)} orgs: "
            f"{total_patterns} patterns, {total_issues} issues"
        )

        return {
            "success": True,
            "orgs_refreshed": len(orgs),
            "patterns_detected": total_patterns,
            "issues_detected": total_issues
        }

    except Exception as e:
        logger.error(f"Failed to refresh portfolio intelligence: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def cleanup_old_dashboard_cache(conn: sqlite3.Connection, days_to_keep: int = 7) -> dict:
    """
    Clean up old dashboard view cache entries

    Args:
        conn: Database connection
        days_to_keep: Number of days to keep cached views

    Returns:
        Stats dict with counts
    """
    logger.info(f"Cleaning up dashboard cache older than {days_to_keep} days")

    try:
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()

        cursor.execute("""
            DELETE FROM dashboard_views
            WHERE generated_at < ?
        """, (cutoff_date,))

        deleted_count = cursor.rowcount

        conn.commit()

        logger.info(f"Deleted {deleted_count} old dashboard cache entries")

        return {"success": True, "deleted_count": deleted_count}

    except Exception as e:
        logger.error(f"Failed to cleanup dashboard cache: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def cleanup_old_snapshots(conn: sqlite3.Connection, days_to_keep: int = 90) -> dict:
    """
    Clean up old health snapshots (keep last 90 days)

    Args:
        conn: Database connection
        days_to_keep: Number of days to keep snapshots

    Returns:
        Stats dict with counts
    """
    logger.info(f"Cleaning up snapshots older than {days_to_keep} days")

    try:
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).date().isoformat()

        # Clean study health snapshots
        cursor.execute("""
            DELETE FROM study_health_snapshots
            WHERE snapshot_date < ?
        """, (cutoff_date,))

        study_snapshots_deleted = cursor.rowcount

        # Clean portfolio health snapshots
        cursor.execute("""
            DELETE FROM portfolio_health_snapshots
            WHERE snapshot_date < ?
        """, (cutoff_date,))

        portfolio_snapshots_deleted = cursor.rowcount

        conn.commit()

        logger.info(
            f"Deleted {study_snapshots_deleted} old study snapshots, "
            f"{portfolio_snapshots_deleted} old portfolio snapshots"
        )

        return {
            "success": True,
            "study_snapshots_deleted": study_snapshots_deleted,
            "portfolio_snapshots_deleted": portfolio_snapshots_deleted
        }

    except Exception as e:
        logger.error(f"Failed to cleanup old snapshots: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def generate_daily_summary_report(stats: dict) -> str:
    """
    Generate daily summary report

    Args:
        stats: Stats from all refresh operations

    Returns:
        Summary report as string
    """
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║           DAILY INTELLIGENCE REFRESH SUMMARY                 ║
╚══════════════════════════════════════════════════════════════╝

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STUDY HEALTH SNAPSHOTS:
  • Studies Refreshed: {stats.get('studies_refreshed', 0)}

PORTFOLIO INTELLIGENCE:
  • Organizations Refreshed: {stats.get('orgs_refreshed', 0)}
  • Cross-Study Patterns Detected: {stats.get('patterns_detected', 0)}
  • Systemic Issues Detected: {stats.get('issues_detected', 0)}

CACHE CLEANUP:
  • Dashboard Cache Entries Deleted: {stats.get('cache_deleted', 0)}
  • Old Study Snapshots Deleted: {stats.get('study_snapshots_deleted', 0)}
  • Old Portfolio Snapshots Deleted: {stats.get('portfolio_snapshots_deleted', 0)}

STATUS: {'✅ SUCCESS' if stats.get('overall_success', False) else '❌ FAILED'}

════════════════════════════════════════════════════════════════
"""
    return report


def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("STARTING DAILY INTELLIGENCE REFRESH")
    logger.info("=" * 80)

    start_time = datetime.now()
    stats = {}

    try:
        conn = get_db_connection()

        # 1. Refresh study health snapshots
        study_stats = refresh_study_health_snapshots(conn)
        stats['studies_refreshed'] = study_stats.get('studies_refreshed', 0)

        # 2. Refresh portfolio intelligence
        portfolio_stats = refresh_portfolio_intelligence(conn)
        stats['orgs_refreshed'] = portfolio_stats.get('orgs_refreshed', 0)
        stats['patterns_detected'] = portfolio_stats.get('patterns_detected', 0)
        stats['issues_detected'] = portfolio_stats.get('issues_detected', 0)

        # 3. Cleanup old dashboard cache
        cache_stats = cleanup_old_dashboard_cache(conn, days_to_keep=7)
        stats['cache_deleted'] = cache_stats.get('deleted_count', 0)

        # 4. Cleanup old snapshots
        snapshot_stats = cleanup_old_snapshots(conn, days_to_keep=90)
        stats['study_snapshots_deleted'] = snapshot_stats.get('study_snapshots_deleted', 0)
        stats['portfolio_snapshots_deleted'] = snapshot_stats.get('portfolio_snapshots_deleted', 0)

        conn.close()

        # Overall success if no errors
        stats['overall_success'] = (
            study_stats.get('success', False) and
            portfolio_stats.get('success', False) and
            cache_stats.get('success', False) and
            snapshot_stats.get('success', False)
        )

    except Exception as e:
        logger.error(f"Critical error in daily intelligence refresh: {e}", exc_info=True)
        stats['overall_success'] = False
        stats['critical_error'] = str(e)

    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    stats['duration_seconds'] = duration

    # Generate and log summary report
    summary = generate_daily_summary_report(stats)
    logger.info("\n" + summary)

    logger.info(f"Daily intelligence refresh completed in {duration:.1f} seconds")
    logger.info("=" * 80)

    # Exit with error code if failed
    if not stats.get('overall_success', False):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
