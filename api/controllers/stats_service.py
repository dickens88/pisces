from sqlalchemy import cast, DateTime, func, case
from datetime import datetime, timedelta, timezone

from models.alert import Alert
from models.incident import Incident
from utils.mysql_conn import Session
from utils.common_utils import format_utc_datetime_to_db_string


class StatisticsService:
    @staticmethod
    def _normalize_datetime_to_utc(dt):
        """
        Normalize datetime to UTC naive datetime.
        Handles any timezone-aware or naive datetime and converts to UTC naive.
        
        Args:
            dt: datetime object (may be timezone-aware or naive)
            
        Returns:
            UTC naive datetime object
        """
        if dt is None:
            return None
        
        # If timezone-aware, convert to UTC then remove timezone info
        if dt.tzinfo is not None:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        
        # If naive, assume it's already UTC
        return dt
    
    @staticmethod
    def _prepare_datetime_for_query(dt):
        """
        Prepare datetime for database query.
        Converts any timezone to UTC and formats as database string.
        
        Args:
            dt: datetime object (may be timezone-aware or naive)
            
        Returns:
            Tuple of (utc_naive_datetime, db_string_format)
            Both can be None if input is None
        """
        if dt is None:
            return None, None
        
        # Normalize to UTC naive datetime
        utc_naive = StatisticsService._normalize_datetime_to_utc(dt)
        
        # Format for database query (ensures UTC timezone in string format)
        db_string = format_utc_datetime_to_db_string(utc_naive.replace(tzinfo=timezone.utc))
        
        return utc_naive, db_string
    @classmethod
    def get_alert_count_by_product_name(cls, start_date, end_date=None, status=None, severity=None,
                                         auto_close=None, verification_state=None, risk_mode=None,
                                         search_keywords=None):
        """Get alert count grouped by product name and is_auto_closed."""
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        with Session() as session:
            closure_type_expr = case(
                (Alert.is_auto_closed == 'Manual', 'Manual'),
                (Alert.is_auto_closed == 'AutoClosed', 'AutoClosed'),
                else_='None'
            )
            
            query = (
                session.query(
                    Alert.data_source_product_name,
                    closure_type_expr.label('closure_type'),
                    func.count(Alert.id).label('count')
                )
                .filter(Alert.create_time >= start_date_str)
            )
            
            if end_date_str:
                query = query.filter(Alert.create_time <= end_date_str)
            
            # Apply filters
            if status and status != 'all':
                status_map = {'open': 'Open', 'block': 'Block', 'closed': 'Closed'}
                query = query.filter(Alert.handle_status == status_map.get(status.lower(), status.capitalize()))
            
            if severity and severity != 'all':
                severity_map = {'fatal': 'Fatal', 'high': 'High', 'medium': 'Medium', 'low': 'Low', 'tips': 'Tips'}
                query = query.filter(Alert.severity == severity_map.get(severity.lower(), severity.capitalize()))
            
            if auto_close and auto_close != 'all':
                query = query.filter(Alert.is_auto_closed == auto_close)
            
            if verification_state and verification_state != 'all':
                query = query.filter(Alert.verification_state == verification_state)
            
            # Apply search keywords (including ipdrr_phase)
            if search_keywords:
                for kw in search_keywords:
                    if isinstance(kw, dict) and 'field' in kw and 'value' in kw:
                        field = kw['field']
                        value = kw['value']
                        if field == 'ipdrr_phase':
                            if value == 'to_incident':
                                query = query.filter(Alert.ipdrr_phase == 'to_incident')
                            elif value == 'not_to_incident':
                                query = query.filter(Alert.ipdrr_phase != 'to_incident')
                        elif field == 'title':
                            query = query.filter(Alert.title.ilike(f"%{value}%"))
                        elif field == 'id':
                            query = query.filter(Alert.alert_id == str(value))
                        elif field == 'creator':
                            query = query.filter(Alert.creator.ilike(f"%{value}%"))
                        elif field == 'actor':
                            query = query.filter(Alert.actor.ilike(f"%{value}%"))
            
            # Apply risk mode filter
            if risk_mode == 'unclosedHighRisk':
                query = query.filter(Alert.handle_status == 'Open')
                query = query.filter(Alert.severity.in_(['Fatal', 'High']))
            
            results = query.group_by(Alert.data_source_product_name, closure_type_expr).all()

        result = {}
        for row in results:
            product_name = row.data_source_product_name or 'Unknown'
            closure_type = row.closure_type or 'None'
            count = int(row.count or 0)
            
            if product_name not in result:
                result[product_name] = {'Manual': 0, 'AutoClosed': 0, 'None': 0}
            
            result[product_name][closure_type] += count
        
        return result

    @classmethod
    def get_alert_status_by_severity(cls, start_date, end_date, status=None, severity=None,
                                      auto_close=None, verification_state=None, risk_mode=None,
                                      search_keywords=None):
        """
        Get alert count grouped by handle_status and severity between start_date and end_date.
        Returns a nested dict:
        {
            "Open": {"Fatal": 1, "High": 2, "Medium": 3, "Low": 0, "Tips": 0},
            "Block": {...},
            "Closed": {...}
        }
        
        Args:
            start_date: Start datetime
            end_date: End datetime
            status: Optional status filter ('open', 'block', 'closed', or None for all)
            severity: Optional severity filter
            auto_close: Optional auto close filter
            verification_state: Optional AI judgment state filter
            risk_mode: Optional risk mode filter
            search_keywords: Optional search keywords list
        """
        # Normalize and format datetime for database query
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)

        # Define standard status and severity buckets to ensure stable keys
        status_buckets = ["Open", "Closed", "Block"]
        severity_buckets = ["Fatal", "High", "Medium", "Low", "Tips"]

        # Initialize result structure with zeros
        result = {
            status: {severity: 0 for severity in severity_buckets}
            for status in status_buckets
        }

        with Session() as session:
            query = (
                session.query(
                    Alert.handle_status.label("status"),
                    Alert.severity.label("severity"),
                    func.count(Alert.id).label("count"),
                )
                .filter(
                    Alert.create_time >= start_date_str,
                    Alert.create_time <= end_date_str,
                )
            )
            
            # Add status filter if provided
            if status and status != 'all':
                # Map frontend status values to database enum values
                status_map = {
                    'open': 'Open',
                    'block': 'Block',
                    'closed': 'Closed'
                }
                db_status = status_map.get(status.lower(), status.capitalize())
                query = query.filter(Alert.handle_status == db_status)
            
            # Apply additional filters
            if severity and severity != 'all':
                severity_map = {'fatal': 'Fatal', 'high': 'High', 'medium': 'Medium', 'low': 'Low', 'tips': 'Tips'}
                query = query.filter(Alert.severity == severity_map.get(severity.lower(), severity.capitalize()))
            
            if auto_close and auto_close != 'all':
                query = query.filter(Alert.is_auto_closed == auto_close)
            
            if verification_state and verification_state != 'all':
                query = query.filter(Alert.verification_state == verification_state)
            
            # Apply search keywords (including ipdrr_phase)
            if search_keywords:
                for kw in search_keywords:
                    if isinstance(kw, dict) and 'field' in kw and 'value' in kw:
                        field = kw['field']
                        value = kw['value']
                        if field == 'ipdrr_phase':
                            if value == 'to_incident':
                                query = query.filter(Alert.ipdrr_phase == 'to_incident')
                            elif value == 'not_to_incident':
                                query = query.filter(Alert.ipdrr_phase != 'to_incident')
                        elif field == 'title':
                            query = query.filter(Alert.title.ilike(f"%{value}%"))
                        elif field == 'id':
                            query = query.filter(Alert.alert_id == str(value))
                        elif field == 'creator':
                            query = query.filter(Alert.creator.ilike(f"%{value}%"))
                        elif field == 'actor':
                            query = query.filter(Alert.actor.ilike(f"%{value}%"))
            
            # Apply risk mode filter
            if risk_mode == 'unclosedHighRisk':
                query = query.filter(Alert.handle_status == 'Open')
                query = query.filter(Alert.severity.in_(['Fatal', 'High']))
            
            query = query.group_by(Alert.handle_status, Alert.severity)

            rows = query.all()

        for row in rows:
            status = row.status or ""
            severity = row.severity or ""

            # Normalize to known buckets, fall back to raw values if unknown
            norm_status = status if status in status_buckets else status
            norm_severity = severity if severity in severity_buckets else severity

            if norm_status not in result:
                result[norm_status] = {}
            if norm_severity not in result[norm_status]:
                result[norm_status][norm_severity] = 0

            result[norm_status][norm_severity] += int(row.count or 0)

        return result

    @classmethod
    def get_alert_trend(cls, start_date, end_date):
        """
        Get alert count grouped by date (day) or hour between start_date and end_date.
        If time range <= 24 hours, group by hour; otherwise group by day.
        Returns a list of dictionaries with 'date' and 'count' keys.
        """
        # Normalize datetime to UTC naive for calculations and format for database query
        start_dt, start_date_str = cls._prepare_datetime_for_query(start_date)
        end_dt, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        # Calculate time difference in hours
        if start_dt is None or end_dt is None:
            return []
        
        time_diff = (end_dt - start_dt).total_seconds() / 3600
        
        with Session() as session:
            # If time range <= 24 hours, group by hour; otherwise group by day
            if time_diff <= 24:
                # Group by hour: extract date and hour from string format
                # Database format: YYYY-MM-DDTHH:mm:ss.SSSZ+0000
                query = (
                    session.query(
                        func.concat(
                            func.substring(Alert.create_time, 1, 10),
                            ' ',
                            func.substring(Alert.create_time, 12, 2),
                            ':00:00'
                        ).label('date'),
                        func.count(Alert.id).label('count')
                    )
                    .filter(
                        Alert.create_time >= start_date_str,
                        Alert.create_time <= end_date_str
                    )
                )
                
                results = query.group_by(
                    func.concat(
                        func.substring(Alert.create_time, 1, 10),
                        ' ',
                        func.substring(Alert.create_time, 12, 2),
                        ':00:00'
                    )
                ).order_by('date').all()
                
                # Convert results to list of dicts
                trend_data = []
                for row in results:
                    date_str = row.date if isinstance(row.date, str) else str(row.date)
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
                # Group by day: extract date from string format
                query = (
                    session.query(
                        func.substring(Alert.create_time, 1, 10).label('date'),
                        func.count(Alert.id).label('count')
                    )
                    .filter(
                        Alert.create_time >= start_date_str,
                        Alert.create_time <= end_date_str
                    )
                )
                
                results = query.group_by(func.substring(Alert.create_time, 1, 10)).order_by('date').all()
                
                # Convert results to list of dicts, ensure date format is YYYY-MM-DD
                trend_data = []
                for row in results:
                    date_str = row.date if isinstance(row.date, str) else str(row.date)
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
        # Normalize datetime to UTC naive for calculations and format for database query
        start_dt, start_date_str = cls._prepare_datetime_for_query(start_date)
        end_dt, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        if start_dt is None or end_dt is None:
            return []
        
        with Session() as session:
            # Group by day: extract date from string format
            query = (
                session.query(
                    func.substring(Incident.create_time, 1, 10).label('date'),
                    func.count(Incident.id).label('count')
                )
                .filter(
                    Incident.create_time >= start_date_str,
                    Incident.create_time <= end_date_str,
                    ~Incident.labels.like('%vulscan%')
                )
            )
            
            results = query.group_by(func.substring(Incident.create_time, 1, 10)).order_by('date').all()
            
            # Convert results to list of dicts, ensure date format is YYYY-MM-DD
            trend_data = []
            for row in results:
                date_str = row.date if isinstance(row.date, str) else str(row.date)
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
        # Normalize datetime to UTC naive for calculations and format for database query
        start_dt, start_date_str = cls._prepare_datetime_for_query(start_date)
        end_dt, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        if start_dt is None or end_dt is None:
            return []
        
        with Session() as session:
            # Group by day: extract date from string format
            # Filter incidents where labels contains 'vulscan'
            query = (
                session.query(
                    func.substring(Incident.create_time, 1, 10).label('date'),
                    func.count(Incident.id).label('count')
                )
                .filter(
                    Incident.create_time >= start_date_str,
                    Incident.create_time <= end_date_str,
                    Incident.labels.like('%vulscan%')
                )
            )
            
            results = query.group_by(func.substring(Incident.create_time, 1, 10)).order_by('date').all()
            
            # Convert results to list of dicts, ensure date format is YYYY-MM-DD
            trend_data = []
            for row in results:
                date_str = row.date if isinstance(row.date, str) else str(row.date)
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
        # Normalize datetime to UTC naive for calculations and format for database query
        start_dt, start_date_str = cls._prepare_datetime_for_query(start_date)
        end_dt, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        if start_dt is None or end_dt is None:
            return []
        
        with Session() as session:
            # Group by day and severity: extract date from string format, severity
            # Filter incidents where labels contains 'vulscan'
            query = (
                session.query(
                    func.substring(Incident.create_time, 1, 10).label('date'),
                    Incident.severity.label('severity'),
                    func.count(Incident.id).label('count')
                )
                .filter(
                    Incident.create_time >= start_date_str,
                    Incident.create_time <= end_date_str,
                    Incident.labels.like('%vulscan%')
                )
            )
            
            results = query.group_by(
                func.substring(Incident.create_time, 1, 10),
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
                date_str = row.date if isinstance(row.date, str) else str(row.date)
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
        # Normalize and format datetime for database query
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        with Session() as session:
            # Group by responsible_dept
            # Filter incidents where labels contains 'vulscan'
            query = (
                session.query(
                    Incident.responsible_dept,
                    func.count(Incident.id).label('count')
                )
                .filter(
                    Incident.create_time >= start_date_str,
                    Incident.create_time <= end_date_str,
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
    def get_incident_trend_by_severity(cls, start_date, end_date):
        """
        Get incident count grouped by date (day) and severity between start_date and end_date.
        Events are incidents where labels field does NOT contain 'vulscan_riskscan'.
        Returns a list of dictionaries with 'date', 'severity', and 'count' keys.
        """
        # Normalize datetime to UTC naive for calculations and format for database query
        start_dt, start_date_str = cls._prepare_datetime_for_query(start_date)
        end_dt, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        if start_dt is None or end_dt is None:
            return []
        
        with Session() as session:
            # Group by day and severity: extract date from string format, severity
            # Filter incidents where labels does NOT contain 'vulscan_riskscan'
            query = (
                session.query(
                    func.substring(Incident.create_time, 1, 10).label('date'),
                    Incident.severity.label('severity'),
                    func.count(Incident.id).label('count')
                )
                .filter(
                    Incident.create_time >= start_date_str,
                    Incident.create_time <= end_date_str,
                    ~Incident.labels.like('%vulscan%')
                )
            )
            
            results = query.group_by(
                func.substring(Incident.create_time, 1, 10),
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
                date_str = row.date if isinstance(row.date, str) else str(row.date)
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
    def get_incident_department_distribution(cls, start_date, end_date):
        """
        Get incident count grouped by responsible department and severity between start_date and end_date.
        Events are incidents where labels field does NOT contain 'vulscan_riskscan'.
        Returns a nested dictionary: {department: {severity: count, ...}, ...}
        """
        # Normalize and format datetime for database query
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        with Session() as session:
            # Group by responsible_dept and severity
            # Filter incidents where labels does NOT contain 'vulscan_riskscan'
            query = (
                session.query(
                    Incident.responsible_dept,
                    Incident.severity,
                    func.count(Incident.id).label('count')
                )
                .filter(
                    Incident.create_time >= start_date_str,
                    Incident.create_time <= end_date_str,
                    ~Incident.labels.like('%vulscan_riskscan%')
                )
                .group_by(Incident.responsible_dept, Incident.severity)
            )
            
            results = query.all()
            
            # Convert results to nested dictionary
            # Handle None/null department names and severity
            distribution = {}
            for row in results:
                dept = row.responsible_dept if row.responsible_dept else 'Unknown'
                severity = row.severity if row.severity else 'Unknown'
                # Normalize severity to capitalize first letter
                severity = severity.capitalize() if severity else 'Unknown'
                
                if dept not in distribution:
                    distribution[dept] = {}
                distribution[dept][severity] = row.count
            
            return distribution

    @classmethod
    def get_incident_root_cause_distribution(cls, start_date, end_date):
        """
        Get incident count grouped by root_cause between start_date and end_date.
        Events are incidents where labels field does NOT contain 'vulscan_riskscan'.
        Returns a dictionary with root_cause names as keys and counts as values.
        """
        # Normalize and format datetime for database query
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        with Session() as session:
            # Group by root_cause
            # Filter incidents where labels does NOT contain 'vulscan_riskscan'
            query = (
                session.query(
                    Incident.root_cause,
                    func.count(Incident.id).label('count')
                )
                .filter(
                    Incident.create_time >= start_date_str,
                    Incident.create_time <= end_date_str,
                    ~Incident.labels.like('%vulscan_riskscan%'),
                    Incident.root_cause.isnot(None),
                    Incident.root_cause != ''
                )
                .group_by(Incident.root_cause)
            )
            
            results = query.all()
            
            # Convert results to dictionary
            # Handle None/null root_cause names as 'Unknown'
            distribution = {}
            for row in results:
                root_cause = row.root_cause if row.root_cause else 'Unknown'
                distribution[root_cause] = row.count
            
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

        # Normalize and format datetime for database query
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)

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
                    Alert.create_time >= start_date_str,
                    Alert.create_time <= end_date_str,
                    Alert.model_name.isnot(None),
                    Alert.model_name != '',
                    Alert.is_ai_decision_correct.isnot(None),
                )
                .group_by(Alert.model_name)
            )

            results = query.all()

        stats = []
        for row in results:
            total_raw = row.total or 0
            correct_raw = row.correct or 0

            total = int(total_raw)
            if total == 0:
                continue
            correct = int(correct_raw)
            accuracy = round((correct / total) * 100.0, 1)
            stats.append({
                'model_name': row.model_name,
                'accuracy': float(accuracy),
                'correct': correct,
                'total': total
            })

        stats.sort(key=lambda item: item['accuracy'], reverse=True)
        return stats[:max(0, limit or 10)]

    @classmethod
    def get_automation_closure_rate(cls, start_date, end_date):
        """
        Get automation closure rate statistics between start_date and end_date.
        Returns:
            dict with keys:
                - total_closed: total number of closed alerts (handle_status='Closed')
                - auto_closed: number of auto-closed alerts (is_auto_closed='AutoClosed')
                - automation_rate: automation closure rate percentage (auto_closed / total_closed * 100)
        """
        # Normalize and format datetime for database query
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        with Session() as session:
            # Count total closed alerts within date range
            query_total = session.query(func.count(Alert.id)).filter(
                Alert.handle_status == 'Closed',
                Alert.create_time >= start_date_str,
                Alert.create_time <= end_date_str
            )
            total_closed = query_total.scalar() or 0
            
            # Count auto-closed alerts within date range
            query_auto = session.query(func.count(Alert.id)).filter(
                Alert.handle_status == 'Closed',
                Alert.is_auto_closed == 'AutoClosed',
                Alert.create_time >= start_date_str,
                Alert.create_time <= end_date_str
            )
            auto_closed = query_auto.scalar() or 0
            
            # Calculate automation rate
            automation_rate = 0.0
            if total_closed > 0:
                automation_rate = round((auto_closed / total_closed) * 100, 1)
            
            return {
                'total_closed': total_closed,
                'auto_closed': auto_closed,
                'automation_rate': automation_rate
            }

    @classmethod
    def get_ai_judgment_coverage_rate(cls, start_date, end_date):
        """
        Get AI judgment coverage rate statistics between start_date and end_date.
        Returns:
            dict with keys:
                - total_alerts: total number of alerts
                - covered_alerts: number of alerts with verification_state != 'Unknown'
                - coverage_rate: coverage rate percentage (covered_alerts / total_alerts * 100)
        """
        # Normalize and format datetime for database query
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        with Session() as session:
            # Count total alerts within date range
            query_total = session.query(func.count(Alert.id)).filter(
                Alert.create_time >= start_date_str,
                Alert.create_time <= end_date_str
            )
            total_alerts = query_total.scalar() or 0
            
            # Count covered alerts (verification_state != 'Unknown')
            query_covered = session.query(func.count(Alert.id)).filter(
                Alert.create_time >= start_date_str,
                Alert.create_time <= end_date_str,
                Alert.verification_state != 'Unknown',
                Alert.verification_state.isnot(None)
            )
            covered_alerts = query_covered.scalar() or 0
            
            # Calculate coverage rate
            coverage_rate = 0.0
            if total_alerts > 0:
                coverage_rate = round((covered_alerts / total_alerts) * 100, 1)
            
            return {
                'total_alerts': total_alerts,
                'covered_alerts': covered_alerts,
                'coverage_rate': coverage_rate
            }

    @classmethod
    def get_ai_judgment_accuracy_rate(cls, start_date, end_date):
        """
        Get AI judgment accuracy rate statistics between start_date and end_date.
        Returns:
            dict with keys:
                - total_judgments: total number of judgments (verification_state != 'Unknown')
                - correct_judgments: number of correct judgments (verification_state != 'Unknown' and is_ai_decision_correct = True)
                - accuracy_rate: accuracy rate percentage (correct_judgments / total_judgments * 100)
        """
        # Normalize and format datetime for database query
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        with Session() as session:
            # Count total judgments (verification_state != 'Unknown')
            query_total = session.query(func.count(Alert.id)).filter(
                Alert.create_time >= start_date_str,
                Alert.create_time <= end_date_str,
                Alert.verification_state != 'Unknown',
                Alert.verification_state.isnot(None)
            )
            total_judgments = query_total.scalar() or 0
            
            # Count correct judgments (verification_state != 'Unknown' and is_ai_decision_correct = True)
            query_correct = session.query(func.count(Alert.id)).filter(
                Alert.create_time >= start_date_str,
                Alert.create_time <= end_date_str,
                Alert.verification_state != 'Unknown',
                Alert.verification_state.isnot(None),
                Alert.is_ai_decision_correct == True
            )
            correct_judgments = query_correct.scalar() or 0
            
            # Calculate accuracy rate
            accuracy_rate = 0.0
            if total_judgments > 0:
                accuracy_rate = round((correct_judgments / total_judgments) * 100, 1)
            
            return {
                'total_judgments': total_judgments,
                'correct_judgments': correct_judgments,
                'accuracy_rate': accuracy_rate
            }