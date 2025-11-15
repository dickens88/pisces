from sqlalchemy import cast, DateTime, func
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
                    cast(Incident.create_time, DateTime) <= end_dt
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