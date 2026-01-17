from datetime import timedelta, timezone

from sqlalchemy import func, case, or_, and_, text

from models.alert import Alert
from models.incident import Incident
from utils.common_utils import normalize_time_to_utc
from utils.mysql_conn import Session


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
        db_string = normalize_time_to_utc(dt)
        
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

    @staticmethod
    @staticmethod
    def _apply_conditions_to_query(query, conditions):
        """
        Apply conditions to a SQLAlchemy query.
        Supports the same condition keys as AlertService.list_local_alerts.
        """
        from sqlalchemy import or_
        
        if not conditions:
            return query
            
        for cond in conditions:
            if not isinstance(cond, dict):
                continue
            for key, value in cond.items():
                if value is None:
                    continue
                val_str = str(value)
                key_lower = key.lower()
                if key_lower == 'title':
                    query = query.filter(Alert.title.ilike(f"%{val_str}%"))
                elif key_lower == 'creator':
                    query = query.filter(Alert.creator.ilike(f"%{val_str}%"))
                elif key_lower == 'actor':
                    query = query.filter(Alert.actor.ilike(f"%{val_str}%"))
                elif key_lower in ('model', 'model_name'):
                    query = query.filter(Alert.model_name == val_str)
                elif key_lower in ('handle_status', 'status'):
                    query = query.filter(Alert.handle_status == val_str)
                elif key_lower == 'severity':
                    query = query.filter(Alert.severity == val_str)
                elif key_lower == 'id':
                    query = query.filter(Alert.alert_id == val_str)
                elif key_lower == 'verification_state':
                    query = query.filter(Alert.verification_state == val_str)
                elif key_lower == 'verification_state!=':
                    query = query.filter(Alert.verification_state != val_str)
                elif key_lower == 'is_ai_decision_correct':
                    if val_str == '':
                        query = query.filter(
                            or_(
                                Alert.is_ai_decision_correct == None,
                                Alert.is_ai_decision_correct == ''
                            )
                        )
                    else:
                        query = query.filter(Alert.is_ai_decision_correct == val_str)
                elif key_lower == 'close_reason':
                    query = query.filter(Alert.close_reason == val_str)
                elif key_lower in ('agent_name', 'agent'):
                    query = query.filter(Alert.agent_name == val_str)
        return query

    @classmethod
    def get_ai_decision_analysis(cls, start_date, end_date, conditions=None):
        """
        Get AI decision analysis statistics by grouping is_ai_decision_correct field.
        Returns count for each value: TP, FP, FN, and empty/null.
        
        Args:
            start_date: Start datetime
            end_date: End datetime
            conditions: Optional list of filter conditions (same format as AlertService.list_local_alerts)
            
        Returns:
            List of dicts with keys: name (TP/FP/FN/Empty), value (count)
        """
        if not start_date or not end_date:
            raise ValueError("start_date and end_date are required")

        # Normalize and format datetime for database query
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)

        with Session() as session:
            # Query to count alerts grouped by is_ai_decision_correct
            query = (
                session.query(
                    Alert.is_ai_decision_correct.label('decision_correct'),
                    func.count(Alert.id).label('count')
                )
                .filter(
                    Alert.create_time >= start_date_str,
                    Alert.create_time <= end_date_str
                )
            )
            
            # Apply conditions if provided
            query = StatisticsService._apply_conditions_to_query(query, conditions)
            
            query = query.group_by(Alert.is_ai_decision_correct)

            results = query.all()

        # Build statistics
        stats = []
        total_count = 0
        
        # Map to store counts for each category
        category_counts = {
            'TP': 0,
            'FP': 0,
            'FN': 0,
            'Empty': 0
        }
        
        for row in results:
            decision_value = row.decision_correct
            count = int(row.count or 0)
            total_count += count
            
            if decision_value == 'TP' or decision_value == 'TT':
                category_counts['TP'] = count
            elif decision_value == 'FP':
                category_counts['FP'] = count
            elif decision_value == 'FN':
                category_counts['FN'] = count
            else:
                # Empty, null, or any other value
                category_counts['Empty'] += count
        
        # Build result list
        for name, value in category_counts.items():
            if value > 0 or name == 'Empty':  # Always include Empty even if 0
                stats.append({
                    'name': name,
                    'value': value
                })
        
        # Calculate total decisions
        total_decisions = sum(item['value'] for item in stats)
        
        return {
            'data': stats,
            'total_decisions': total_decisions
        }

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
    def get_ai_judgment_coverage_rate(cls, start_date, end_date, conditions=None):
        """
        Get AI judgment coverage rate statistics between start_date and end_date.
        Args:
            start_date: Start datetime
            end_date: End datetime
            conditions: Optional list of filter conditions (same format as AlertService.list_local_alerts)
        Returns:
            dict with keys:
                - total_alerts: total number of alerts (excluding is_auto_closed='AutoClosed')
                - covered_alerts: number of alerts with verification_state != 'Unknown' (excluding is_auto_closed='AutoClosed')
                - coverage_rate: coverage rate percentage (covered_alerts / total_alerts * 100)
        """
        # Normalize and format datetime for database query
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        with Session() as session:
            # Count total alerts within date range (excluding is_auto_closed='AutoClosed')
            query_total = session.query(func.count(Alert.id)).filter(
                Alert.create_time >= start_date_str,
                Alert.create_time <= end_date_str,
                or_(Alert.is_auto_closed != 'AutoClosed', Alert.is_auto_closed.is_(None))
            )
            # Apply conditions if provided
            query_total = cls._apply_conditions_to_query(query_total, conditions)
            total_alerts = query_total.scalar() or 0
            
            # Count covered alerts (verification_state != 'Unknown', excluding is_auto_closed='AutoClosed')
            query_covered = session.query(func.count(Alert.id)).filter(
                Alert.create_time >= start_date_str,
                Alert.create_time <= end_date_str,
                Alert.verification_state != 'Unknown',
                Alert.verification_state.isnot(None),
                or_(Alert.is_auto_closed != 'AutoClosed', Alert.is_auto_closed.is_(None))
            )
            # Apply conditions if provided
            query_covered = cls._apply_conditions_to_query(query_covered, conditions)
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
                - total_judgments: total number of judgments (verification_state != 'Unknown', excluding is_auto_closed='AutoClosed')
                - correct_judgments: number of correct judgments (verification_state != 'Unknown' and is_ai_decision_correct = 'TP' or 'TT', excluding is_auto_closed='AutoClosed')
                - accuracy_rate: accuracy rate percentage (correct_judgments / total_judgments * 100)
        """
        # Normalize and format datetime for database query
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        with Session() as session:
            # Count total judgments (verification_state != 'Unknown', excluding is_auto_closed='AutoClosed')
            query_total = session.query(func.count(Alert.id)).filter(
                Alert.create_time >= start_date_str,
                Alert.create_time <= end_date_str,
                Alert.verification_state != 'Unknown',
                Alert.verification_state.isnot(None),
                or_(Alert.is_auto_closed != 'AutoClosed', Alert.is_auto_closed.is_(None))
            )
            total_judgments = query_total.scalar() or 0
            
            # Count correct judgments (verification_state != 'Unknown' and is_ai_decision_correct = 'TP' or 'TT', excluding is_auto_closed='AutoClosed')
            query_correct = session.query(func.count(Alert.id)).filter(
                Alert.create_time >= start_date_str,
                Alert.create_time <= end_date_str,
                Alert.verification_state != 'Unknown',
                Alert.verification_state.isnot(None),
                or_(Alert.is_ai_decision_correct == 'TP', Alert.is_ai_decision_correct == 'TT'),
                or_(Alert.is_auto_closed != 'AutoClosed', Alert.is_auto_closed.is_(None))
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

    @classmethod
    def get_ai_accuracy_trend_by_model(cls, start_date, end_date, conditions=None):
        """
        Get AI accuracy trend grouped by date and model_name between start_date and end_date.
        Accuracy calculation:
        - Numerator: count of is_ai_decision_correct='TP'
        - Denominator: count of verification_state != 'Unknown'
        
        Returns a list of dictionaries with 'date', 'model_name', and 'accuracy' keys.
        Uses raw SQL for better performance and simpler code.
        """
        # Normalize datetime to UTC naive for calculations and format for database query
        start_dt, start_date_str = cls._prepare_datetime_for_query(start_date)
        end_dt, end_date_str = cls._prepare_datetime_for_query(end_date)
        
        if start_dt is None or end_dt is None:
            return []
        
        # Build WHERE conditions (create_time is stored as string, use SUBSTRING for date extraction)
        where_conditions = [
            "SUBSTRING(create_time, 1, 10) >= :start_date",
            "SUBSTRING(create_time, 1, 10) <= :end_date",
            "model_name IS NOT NULL",
            "model_name != ''"
        ]
        
        # Build condition filters from conditions parameter
        condition_params = {}
        if conditions:
            for cond in conditions:
                if not isinstance(cond, dict):
                    continue
                for key, value in cond.items():
                    if value is None:
                        continue
                    key_lower = key.lower()
                    if key_lower in ('model', 'model_name'):
                        where_conditions.append("model_name = :model_name")
                        condition_params['model_name'] = str(value)
                    elif key_lower == 'verification_state':
                        where_conditions.append("verification_state = :verification_state")
                        condition_params['verification_state'] = str(value)
                    elif key_lower == 'verification_state!=':
                        where_conditions.append("verification_state != :verification_state_ne")
                        condition_params['verification_state_ne'] = str(value)
                    elif key_lower == 'is_ai_decision_correct':
                        if str(value) == '':
                            where_conditions.append("(is_ai_decision_correct IS NULL OR is_ai_decision_correct = '')")
                        else:
                            where_conditions.append("is_ai_decision_correct = :is_ai_decision_correct")
                            condition_params['is_ai_decision_correct'] = str(value)
        
        where_clause = " AND ".join(where_conditions)
        
        # Use raw SQL to calculate accuracy directly in database
        # create_time is stored as string format: YYYY-MM-DDTHH:mm:ss.SSSZ+0000
        # First, get top 5 model_names by total_count (denominator)
        # Then filter results to only include these top 5 models
        sql = text(f"""
            WITH model_totals AS (
                SELECT 
                    COALESCE(model_name, 'Unknown') as model_name,
                    SUM(CASE WHEN verification_state IS NOT NULL AND verification_state != 'Unknown' THEN 1 ELSE 0 END) as total_count
                FROM t_alerts
                WHERE {where_clause}
                GROUP BY COALESCE(model_name, 'Unknown')
                ORDER BY total_count DESC
                LIMIT 5
            ),
            trend_data AS (
                SELECT 
                    SUBSTRING(create_time, 1, 10) as date,
                    COALESCE(a.model_name, 'Unknown') as model_name,
                    SUM(CASE WHEN a.is_ai_decision_correct IN ('TP', 'TT') THEN 1 ELSE 0 END) as tp_count,
                    SUM(CASE WHEN a.verification_state IS NOT NULL AND a.verification_state != 'Unknown' THEN 1 ELSE 0 END) as total_count,
                    CASE 
                        WHEN SUM(CASE WHEN a.verification_state IS NOT NULL AND a.verification_state != 'Unknown' THEN 1 ELSE 0 END) > 0
                        THEN ROUND(
                            SUM(CASE WHEN a.is_ai_decision_correct IN ('TP', 'TT') THEN 1 ELSE 0 END) * 100.0 / 
                            SUM(CASE WHEN a.verification_state IS NOT NULL AND a.verification_state != 'Unknown' THEN 1 ELSE 0 END),
                            2
                        )
                        ELSE 0.0
                    END as accuracy
                FROM t_alerts a
                WHERE {where_clause}
                GROUP BY SUBSTRING(a.create_time, 1, 10), COALESCE(a.model_name, 'Unknown')
            )
            SELECT 
                td.date,
                td.model_name,
                td.tp_count,
                td.total_count,
                td.accuracy
            FROM trend_data td
            INNER JOIN model_totals mt ON td.model_name = mt.model_name
            ORDER BY td.date, td.model_name
        """)
        
        with Session() as session:
            params = {
                'start_date': start_date_str[:10] if start_date_str else None,
                'end_date': end_date_str[:10] if end_date_str else None,
                **condition_params
            }
            
            result = session.execute(sql, params)
            rows = result.fetchall()
            
            # Convert to list of dicts
            trend_data = []
            for row in rows:
                trend_data.append({
                    'date': str(row.date),
                    'model_name': row.model_name or 'Unknown',
                    'accuracy': float(row.accuracy or 0.0),
                    'tp_count': int(row.tp_count or 0),
                    'total_count': int(row.total_count or 0)
                })
            
            # Fill in missing dates with 0 accuracy for each model
            # Get all unique dates and model names
            all_dates = set()
            all_models = set()
            current_date = start_dt.date()
            end_date_obj = end_dt.date()
            
            while current_date <= end_date_obj:
                date_str = current_date.strftime('%Y-%m-%d')
                all_dates.add(date_str)
                current_date += timedelta(days=1)
            
            # Add models from actual data
            for item in trend_data:
                if item['model_name']:
                    all_models.add(item['model_name'])
            
            # Build a dictionary for quick lookup
            trend_dict = {}
            for item in trend_data:
                date = item['date']
                model_name = item['model_name']
                if date not in trend_dict:
                    trend_dict[date] = {}
                trend_dict[date][model_name] = {
                    'accuracy': item['accuracy'],
                    'tp_count': item['tp_count'],
                    'total_count': item['total_count']
                }
            
            # Build complete trend data
            complete_trend = []
            for date in sorted(all_dates):
                for model_name in sorted(all_models):
                    data = trend_dict.get(date, {}).get(model_name, {
                        'accuracy': 0.0,
                        'tp_count': 0,
                        'total_count': 0
                    })
                    complete_trend.append({
                        'date': date,
                        'model_name': model_name,
                        'accuracy': data['accuracy'],
                        'tp_count': data['tp_count'],
                        'total_count': data['total_count']
                    })
            
            return complete_trend

    @classmethod
    def get_model_performance(cls, start_date, end_date, conditions=None):
        """
        Get AI performance statistics grouped by model_name and agent_name.
        
        Args:
            start_date: Start datetime
            end_date: End datetime
            conditions: Optional list of filter conditions (same format as AlertService.list_local_alerts)
            
        Returns:
            List of dicts with keys:
                - model_name: Model name
                - agent_name: Agent name
                - handled_count: Count of alerts with verification_state != 'Unknown' (excluding is_auto_closed='AutoClosed')
                - correct_decisions_count: Count of TP (is_ai_decision_correct = 'TP')
                - false_positive_count: Count of FP (is_ai_decision_correct = 'FP')
                - false_negative_count: Count of FN (is_ai_decision_correct = 'FN')
                - total_count: Total count of alerts (excluding is_auto_closed='AutoClosed')
                - coverage_rate: handled_count / total_count * 100
        """
        if not start_date or not end_date:
            raise ValueError("start_date and end_date are required")

        # Normalize and format datetime for database query
        _, start_date_str = cls._prepare_datetime_for_query(start_date)
        _, end_date_str = cls._prepare_datetime_for_query(end_date)

        with Session() as session:
            # Query to get statistics grouped by model_name and agent_name
            query = (
                session.query(
                    func.coalesce(Alert.model_name, 'Unknown Model').label('model_name'),
                    func.coalesce(Alert.agent_name, 'Unknown Agent').label('agent_name'),
                    func.count(Alert.id).label('total_count'),
                    func.sum(
                        case(
                            (
                                and_(
                                    Alert.verification_state != 'Unknown',
                                    Alert.verification_state.isnot(None)
                                ),
                                1
                            ),
                            else_=0
                        )
                    ).label('handled_count'),
                    func.sum(
                        case(
                            (Alert.is_ai_decision_correct == 'TP', 1),
                            else_=0
                        )
                    ).label('correct_decisions_count'),
                    func.sum(
                        case(
                            (Alert.is_ai_decision_correct == 'FP', 1),
                            else_=0
                        )
                    ).label('false_positive_count'),
                    func.sum(
                        case(
                            (Alert.is_ai_decision_correct == 'FN', 1),
                            else_=0
                        )
                    ).label('false_negative_count')
                )
                .filter(
                    Alert.create_time >= start_date_str,
                    Alert.create_time <= end_date_str,
                    or_(Alert.is_auto_closed != 'AutoClosed', Alert.is_auto_closed.is_(None))
                )
            )
            
            # Apply conditions if provided
            query = StatisticsService._apply_conditions_to_query(query, conditions)
            
            query = query.group_by(
                func.coalesce(Alert.model_name, 'Unknown Model'),
                func.coalesce(Alert.agent_name, 'Unknown Agent')
            )

            results = query.all()

        # Build result list
        stats = []
        for row in results:
            model_name = row.model_name or 'Unknown Model'
            agent_name = row.agent_name or 'Unknown Agent'
            total_count = int(row.total_count or 0)
            handled_count = int(row.handled_count or 0)
            correct_decisions_count = int(row.correct_decisions_count or 0)
            false_positive_count = int(row.false_positive_count or 0)
            false_negative_count = int(row.false_negative_count or 0)
            
            # Calculate coverage rate
            coverage_rate = 0.0
            if total_count > 0:
                coverage_rate = round((handled_count / total_count) * 100, 1)
            
            stats.append({
                'model_name': model_name,
                'agent_name': agent_name,
                'handled_count': handled_count,
                'correct_decisions_count': correct_decisions_count,
                'false_positive_count': false_positive_count,
                'false_negative_count': false_negative_count,
                'total_count': total_count,
                'coverage_rate': coverage_rate
            })
        
        return stats