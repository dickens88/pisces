from sqlalchemy import cast, DateTime, func

from models.alert import Alert
from utils.mysql_conn import Session


class StatisticsService:
    @classmethod
    def get_alert_count_by_product_name(cls, start_date):
        """Get alert count grouped by product name since start_date."""
        with Session() as session:
            results = (
                session.query(Alert.data_source_product_name, func.count(Alert.id))
                .filter(cast(Alert.create_time, DateTime)>=start_date)
                .group_by(Alert.data_source_product_name)
                .all()
            )

        return dict(results)