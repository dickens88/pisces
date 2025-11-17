from sqlalchemy import cast, DateTime, func, case
from datetime import datetime, timedelta

from models.alert import Alert
from models.incident import Incident
from utils.mysql_conn import Session


class StatisticsService:
    @classmethod
    def get_alert_count_by_product_name(cls, start_date, end_date=None, status=None):
        """Get alert count grouped by product name between start_date and end_date, optionally filtered by status."""
        with Session() as session:
            query = (
                session.query(Alert.data_source_product_name, func.count(Alert.id))
                .filter(cast(Alert.create_time, DateTime) >= start_date)
            )
            
            # Add end_date filter if provided
            if end_date:
                query = query.filter(cast(Alert.create_time, DateTime) <= end_date)
            
            # Add status filter if provided
            # Convert frontend status (lowercase) to database format (capitalized)
            if status and status != 'all':
                # Map frontend status values to database enum values
                status_map = {
                    'open': 'Open',
                    'block': 'Block',
                    'closed': 'Closed'
                }
                db_status = status_map.get(status.lower(), status.capitalize())
                query = query.filter(Alert.handle_status == db_status)
            
            results = query.group_by(Alert.data_source_product_name).all()

        return dict(results)

    @classmethod
    def get_alert_trend(cls, start_date, end_date):
        """
        Get alert count grouped by date (day) or hour between start_date and end_date.
        If time range <= 24 hours, group by hour; otherwise group by day.
        Returns a list of dictionaries with 'date' and 'count' keys.
        """
        # Parse dates
        if isinstance(start_date, str):
            start_dt = datetime.fromisoformat(start_date)
        elif isinstance(start_date, datetime):
            start_dt = start_date
        else:
            start_dt = start_date
        
        if isinstance(end_date, str):
            end_dt = datetime.fromisoformat(end_date)
        elif isinstance(end_date, datetime):
            end_dt = end_date
        else:
            end_dt = end_date
        
        # Calculate time difference in hours
        time_diff = (end_dt - start_dt).total_seconds() / 3600
        
        with Session() as session:
            # If time range <= 24 hours, group by hour; otherwise group by day
            if time_diff <= 24:
                # Group by hour: DATE_FORMAT(create_time, '%Y-%m-%d %H:00:00')
                query = (
                    session.query(
                        func.date_format(cast(Alert.create_time, DateTime), '%Y-%m-%d %H:00:00').label('date'),
                        func.count(Alert.id).label('count')
                    )
                    .filter(
                        cast(Alert.create_time, DateTime) >= start_dt,
                        cast(Alert.create_time, DateTime) <= end_dt
                    )
                )
                
                results = query.group_by(func.date_format(cast(Alert.create_time, DateTime), '%Y-%m-%d %H:00:00')).order_by('date').all()
                
                # Convert results to list of dicts
                trend_data = []
                for row in results:
                    date_str = row.date if isinstance(row.date, str) else row.date.strftime('%Y-%m-%d %H:00:00')
                    trend_data.append({'date': date_str, 'count': row.count})
                
                # Fill in missing hours with 0 count
                trend_dict = {item['date']: item['count'] for item in trend_data}
                complete_trend = []
                current_time = start_dt.replace(minute=0, second=0, microsecond=0)
                end_time = end_dt.replace(minute=0, second=0, microsecond=0)
                
                while current_time <= end_time:
                    date_str = current_time.strftime('%Y-%m-%d %H:00:00')
                    complete_trend.append({
                        'date': date_str,
                        'count': trend_dict.get(date_str, 0)
                    })
                    current_time += timedelta(hours=1)
                
                return complete_trend
            else:
                # Group by day: DATE(create_time)
                query = (
                    session.query(
                        func.date(cast(Alert.create_time, DateTime)).label('date'),
                        func.count(Alert.id).label('count')
                    )
                    .filter(
                        cast(Alert.create_time, DateTime) >= start_dt,
                        cast(Alert.create_time, DateTime) <= end_dt
                    )
                )
                
                results = query.group_by(func.date(cast(Alert.create_time, DateTime))).order_by('date').all()
                
                # Convert results to list of dicts, ensure date format is YYYY-MM-DD
                trend_data = []
                for row in results:
                    date_obj = row.date
                    if isinstance(date_obj, str):
                        date_str = date_obj
                    else:
                        date_str = date_obj.strftime('%Y-%m-%d') if hasattr(date_obj, 'strftime') else str(date_obj)
                    trend_data.append({'date': date_str, 'count': row.count})
                
                # Fill in missing dates with 0 count
                trend_dict = {item['date']: item['count'] for item in trend_data}
                complete_trend = []
                current_date = start_dt.date()
                end_date_obj = end_dt.date()
                
                while current_date <= end_date_obj:
                    date_str = current_date.strftime('%Y-%m-%d')
                    complete_trend.append({
                        'date': date_str,
                        'count': trend_dict.get(date_str, 0)
                    })
                    current_date += timedelta(days=1)
                
                return complete_trend

    @classmethod
    def get_incident_trend(cls, start_date, end_date):
        """
        Get incident count grouped by date (day) between start_date and end_date.
        Returns a list of dictionaries with 'date' and 'count' keys.
        """
        # Parse dates
        if isinstance(start_date, str):
            start_dt = datetime.fromisoformat(start_date)
        elif isinstance(start_date, datetime):
            start_dt = start_date
        else:
            start_dt = start_date
        
        if isinstance(end_date, str):
            end_dt = datetime.fromisoformat(end_date)
        elif isinstance(end_date, datetime):
            end_dt = end_date
        else:
            end_dt = end_date
        
        with Session() as session:
            # Group by day: DATE(create_time)
            query = (
                session.query(
                    func.date(cast(Incident.create_time, DateTime)).label('date'),
                    func.count(Incident.id).label('count')
                )
                .filter(
                    cast(Incident.create_time, DateTime) >= start_dt,
                    cast(Incident.create_time, DateTime) <= end_dt,
                    ~Incident.labels.like('%vulscan%')
                )
            )
            
            results = query.group_by(func.date(cast(Incident.create_time, DateTime))).order_by('date').all()
            
            # Convert results to list of dicts, ensure date format is YYYY-MM-DD
            trend_data = []
            for row in results:
                date_obj = row.date
                if isinstance(date_obj, str):
                    date_str = date_obj
                else:
                    date_str = date_obj.strftime('%Y-%m-%d') if hasattr(date_obj, 'strftime') else str(date_obj)
                trend_data.append({'date': date_str, 'count': row.count})
            
            # Fill in missing dates with 0 count
            trend_dict = {item['date']: item['count'] for item in trend_data}
            complete_trend = []
            current_date = start_dt.date()
            end_date_obj = end_dt.date()
            
            while current_date <= end_date_obj:
                date_str = current_date.strftime('%Y-%m-%d')
                complete_trend.append({
                    'date': date_str,
                    'count': trend_dict.get(date_str, 0)
                })
                current_date += timedelta(days=1)
            
            return complete_trend

    @classmethod
    def get_vulnerability_trend(cls, start_date, end_date):
        """
        Get vulnerability count grouped by date (day) between start_date and end_date.
        Vulnerabilities are incidents where labels field contains 'vulscan'.
        Returns a list of dictionaries with 'date' and 'count' keys.
        """
        # Parse dates
        if isinstance(start_date, str):
            start_dt = datetime.fromisoformat(start_date)
        elif isinstance(start_date, datetime):
            start_dt = start_date
        else:
            start_dt = start_date
        
        if isinstance(end_date, str):
            end_dt = datetime.fromisoformat(end_date)
        elif isinstance(end_date, datetime):
            end_dt = end_date
        else:
            end_dt = end_date
        
        with Session() as session:
            # Group by day: DATE(create_time)
            # Filter incidents where labels contains 'vulscan'
            query = (
                session.query(
                    func.date(cast(Incident.create_time, DateTime)).label('date'),
                    func.count(Incident.id).label('count')
                )
                .filter(
                    cast(Incident.create_time, DateTime) >= start_dt,
                    cast(Incident.create_time, DateTime) <= end_dt,
                    Incident.labels.like('%vulscan%')
                )
            )
            
            results = query.group_by(func.date(cast(Incident.create_time, DateTime))).order_by('date').all()
            
            # Convert results to list of dicts, ensure date format is YYYY-MM-DD
            trend_data = []
            for row in results:
                date_obj = row.date
                if isinstance(date_obj, str):
                    date_str = date_obj
                else:
                    date_str = date_obj.strftime('%Y-%m-%d') if hasattr(date_obj, 'strftime') else str(date_obj)
                trend_data.append({'date': date_str, 'count': row.count})
            
            # Fill in missing dates with 0 count
            trend_dict = {item['date']: item['count'] for item in trend_data}
            complete_trend = []
            current_date = start_dt.date()
            end_date_obj = end_dt.date()
            
            while current_date <= end_date_obj:
                date_str = current_date.strftime('%Y-%m-%d')
                complete_trend.append({
                    'date': date_str,
                    'count': trend_dict.get(date_str, 0)
                })
                current_date += timedelta(days=1)
            
            return complete_trend

    @classmethod
    def get_vulnerability_trend_by_severity(cls, start_date, end_date):
        """
        Get vulnerability count grouped by date (day) and severity between start_date and end_date.
        Vulnerabilities are incidents where labels field contains 'vulscan'.
        Returns a list of dictionaries with 'date', 'severity', and 'count' keys.
        """
        # Parse dates
        if isinstance(start_date, str):
            start_dt = datetime.fromisoformat(start_date)
        elif isinstance(start_date, datetime):
            start_dt = start_date
        else:
            start_dt = start_date
        
        if isinstance(end_date, str):
            end_dt = datetime.fromisoformat(end_date)
        elif isinstance(end_date, datetime):
            end_dt = end_date
        else:
            end_dt = end_date
        
        with Session() as session:
            # Group by day and severity: DATE(create_time), severity
            # Filter incidents where labels contains 'vulscan'
            query = (
                session.query(
                    func.date(cast(Incident.create_time, DateTime)).label('date'),
                    Incident.severity.label('severity'),
                    func.count(Incident.id).label('count')
                )
                .filter(
                    cast(Incident.create_time, DateTime) >= start_dt,
                    cast(Incident.create_time, DateTime) <= end_dt,
                    Incident.labels.like('%vulscan%')
                )
            )
            
            results = query.group_by(
                func.date(cast(Incident.create_time, DateTime)),
                Incident.severity
            ).order_by('date', 'severity').all()
            
            # Convert results to list of dicts, ensure date format is YYYY-MM-DD
            # Normalize severity to capitalize first letter (e.g., 'high' -> 'High')
            def normalize_severity(severity):
                if not severity:
                    return 'Unknown'
                # Capitalize first letter, keep rest lowercase
                return severity.capitalize() if severity else 'Unknown'
            
            trend_data = []
            for row in results:
                date_obj = row.date
                if isinstance(date_obj, str):
                    date_str = date_obj
                else:
                    date_str = date_obj.strftime('%Y-%m-%d') if hasattr(date_obj, 'strftime') else str(date_obj)
                trend_data.append({
                    'date': date_str,
                    'severity': normalize_severity(row.severity),
                    'count': row.count
                })
            
            # Fill in missing dates and severities with 0 count
            # Get all unique dates and severities
            all_dates = set()
            # Standard severity levels (capitalized)
            all_severities = set(['Critical', 'High', 'Medium', 'Low', 'Unknown'])
            current_date = start_dt.date()
            end_date_obj = end_dt.date()
            
            while current_date <= end_date_obj:
                date_str = current_date.strftime('%Y-%m-%d')
                all_dates.add(date_str)
                current_date += timedelta(days=1)
            
            # Add severities from actual data (already normalized)
            for item in trend_data:
                if item['severity']:
                    all_severities.add(item['severity'])
            
            # Build a dictionary for quick lookup: {date: {severity: count}}
            trend_dict = {}
            for item in trend_data:
                date = item['date']
                severity = item['severity']
                count = item['count']
                if date not in trend_dict:
                    trend_dict[date] = {}
                trend_dict[date][severity] = count
            
            # Build complete trend data
            complete_trend = []
            for date in sorted(all_dates):
                for severity in sorted(all_severities):
                    count = trend_dict.get(date, {}).get(severity, 0)
                    complete_trend.append({
                        'date': date,
                        'severity': severity,
                        'count': count
                    })
            
            return complete_trend

    @classmethod
    def get_vulnerability_department_distribution(cls, start_date, end_date):
        """
        Get vulnerability count grouped by responsible department between start_date and end_date.
        Vulnerabilities are incidents where labels field contains 'vulscan'.
        Returns a dictionary with department names as keys and counts as values.
        """
        # Parse dates
        if isinstance(start_date, str):
            start_dt = datetime.fromisoformat(start_date)
        elif isinstance(start_date, datetime):
            start_dt = start_date
        else:
            start_dt = start_date
        
        if isinstance(end_date, str):
            end_dt = datetime.fromisoformat(end_date)
        elif isinstance(end_date, datetime):
            end_dt = end_date
        else:
            end_dt = end_date
        
        with Session() as session:
            # Group by responsible_dept
            # Filter incidents where labels contains 'vulscan'
            query = (
                session.query(
                    Incident.responsible_dept,
                    func.count(Incident.id).label('count')
                )
                .filter(
                    cast(Incident.create_time, DateTime) >= start_dt,
                    cast(Incident.create_time, DateTime) <= end_dt,
                    Incident.labels.like('%vulscan%')
                )
                .group_by(Incident.responsible_dept)
            )
            
            results = query.all()
            
            # Convert results to dictionary
            # Handle None/null department names as 'Unknown' or empty string
            distribution = {}
            for row in results:
                dept = row.responsible_dept if row.responsible_dept else 'Unknown'
                distribution[dept] = row.count
            
            return distribution

    @classmethod
    def get_ai_accuracy_by_model(cls, start_date, end_date, limit=10):
        """
        Calculate AI decision accuracy per model between start_date and end_date.
        Only includes alerts with non-null model_name and is_ai_decision_correct.
        Returns at most `limit` models sorted by accuracy (desc).
        """
        if not start_date or not end_date:
            raise ValueError("start_date and end_date are required")

        if isinstance(start_date, str):
            start_dt = datetime.fromisoformat(start_date)
        elif isinstance(start_date, datetime):
            start_dt = start_date
        else:
            start_dt = start_date

        if isinstance(end_date, str):
            end_dt = datetime.fromisoformat(end_date)
        elif isinstance(end_date, datetime):
            end_dt = end_date
        else:
            end_dt = end_date

        with Session() as session:
            query = (
                session.query(
                    Alert.model_name.label('model_name'),
                    func.count(Alert.id).label('total'),
                    func.sum(
                        case(
                            (Alert.is_ai_decision_correct == True, 1),
                            else_=0
                        )
                    ).label('correct')
                )
                .filter(
                    cast(Alert.create_time, DateTime) >= start_dt,
                    cast(Alert.create_time, DateTime) <= end_dt,
                    Alert.model_name.isnot(None),
                    Alert.model_name != '',
                    Alert.is_ai_decision_correct.isnot(None),
                )
                .group_by(Alert.model_name)
            )

            results = query.all()

        stats = []
        for row in results:
            total = row.total or 0
            if total == 0:
                continue
            correct = row.correct or 0
            accuracy = round((correct / total) * 100, 1)
            stats.append({
                'model_name': row.model_name,
                'accuracy': accuracy,
                'correct': int(correct),
                'total': int(total)
            })

        stats.sort(key=lambda item: item['accuracy'], reverse=True)
        return stats[:max(0, limit or 10)]

    @classmethod
    def get_automation_closure_rate(cls):
        """
        Get automation closure rate statistics.
        Returns:
            dict with keys:
                - total_closed: total number of closed alerts (handle_status='Closed')
                - auto_closed: number of auto-closed alerts (is_auto_closed='AutoClosed')
                - automation_rate: automation closure rate percentage (auto_closed / total_closed * 100)
        """
        with Session() as session:
            # Count total closed alerts
            total_closed = session.query(func.count(Alert.id)).filter(
                Alert.handle_status == 'Closed'
            ).scalar() or 0
            
            # Count auto-closed alerts
            auto_closed = session.query(func.count(Alert.id)).filter(
                Alert.handle_status == 'Closed',
                Alert.is_auto_closed == 'AutoClosed'
            ).scalar() or 0
            
            # Calculate automation rate
            automation_rate = 0.0
            if total_closed > 0:
                automation_rate = round((auto_closed / total_closed) * 100, 1)
            
            return {
                'total_closed': total_closed,
                'auto_closed': auto_closed,
                'automation_rate': automation_rate
            }