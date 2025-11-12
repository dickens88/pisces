import datetime

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from models import user
from utils.common_utils import generate_random_string
from views import auth_view, alert_view
from views import mock_alert_view, mock_dashboard_view, mock_incident_view, mock_vulnerability_view

app = Flask(__name__)
app.config.from_object(__name__)
api = Api(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})
app.config['JWT_SECRET_KEY'] = generate_random_string()
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=2)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(minutes=130)

jwt = JWTManager(app)
app.config['JWT_BLOCKLIST_TOKEN_CHECKS'] = ['access']


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, decrypted_token):
    jti = decrypted_token['jti']
    return user.RevokedTokenModel.is_jti_blacklisted(jti)


api.add_resource(auth_view.UserLogin, '/login')
api.add_resource(auth_view.UserLogoutAccess, '/logout')
api.add_resource(auth_view.UserRefresh, '/refresh')
api.add_resource(auth_view.UserView, '/user/password')
api.add_resource(auth_view.UserManagement, '/user/management')

api.add_resource(alert_view.AlertView, *['/api/alerts', '/api/alerts/<alert_id>'])
api.add_resource(alert_view.AlertCreateView, '/api/alerts/create')

# Mock API路由 - 告警相关
# api.add_resource(mock_alert_view.MockAlertListView, '/api/alerts')
api.add_resource(mock_alert_view.MockAlertDetailView, '/api/alerts/<int:alert_id>')
api.add_resource(mock_alert_view.MockAlertStatisticsView, '/api/alerts/statistics')
api.add_resource(mock_alert_view.MockBatchCloseAlertsView, '/api/alerts/batch-close')
api.add_resource(mock_alert_view.MockOpenAlertView, '/api/alerts/<int:alert_id>/open')
api.add_resource(mock_alert_view.MockAssociateAlertsToIncidentView, '/api/alerts/associate')
api.add_resource(mock_alert_view.MockThreatIntelligenceView, '/api/alerts/<int:alert_id>/threat-intelligence')
api.add_resource(mock_alert_view.MockAssociatedAlertsView, '/api/alerts/<int:alert_id>/associated')
# api.add_resource(mock_alert_view.MockCreateAlertView, '/api/alerts/create')
api.add_resource(mock_alert_view.MockUpdateAlertView, '/api/alerts/<int:alert_id>/update')

# Mock API路由 - 仪表板相关
api.add_resource(mock_dashboard_view.MockDashboardStatisticsView, '/api/dashboard/statistics')
api.add_resource(mock_dashboard_view.MockRecentOpenAlertsView, '/api/dashboard/recent-alerts')
api.add_resource(mock_dashboard_view.MockRecentOpenVulnerabilitiesView, '/api/dashboard/recent-vulnerabilities')

# Mock API路由 - 事件相关
api.add_resource(mock_incident_view.MockIncidentListView, '/api/incidents')
api.add_resource(mock_incident_view.MockIncidentDetailView, '/api/incidents/<int:incident_id>')
api.add_resource(mock_incident_view.MockBatchCloseIncidentsView, '/api/incidents/batch-close')
api.add_resource(mock_incident_view.MockCreateIncidentView, '/api/incidents/create')
api.add_resource(mock_incident_view.MockUpdateIncidentView, '/api/incidents/<int:incident_id>/update')

# Mock API路由 - 漏洞相关
api.add_resource(mock_vulnerability_view.MockVulnerabilityListView, '/api/vulnerabilities')
api.add_resource(mock_vulnerability_view.MockVulnerabilityDetailView, '/api/vulnerabilities/<int:vulnerability_id>')
api.add_resource(mock_vulnerability_view.MockVulnerabilityTrendView, '/api/vulnerabilities/trend')
api.add_resource(mock_vulnerability_view.MockVulnerabilityDepartmentDistributionView, '/api/vulnerabilities/department-distribution')
api.add_resource(mock_vulnerability_view.MockBatchOperateVulnerabilitiesView, '/api/vulnerabilities/batch-operate')
api.add_resource(mock_vulnerability_view.MockExportVulnerabilityReportView, '/api/vulnerabilities/export')


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['SCHEDULER_EXECUTORS'] = {
        'default': {'type': 'threadpool', 'max_workers': 30}
    }
    # scheduler.api_enabled = True
    # scheduler.init_app(app)
    # scheduler.start()

    app.run(debug=True, host='0.0.0.0', port=8080)
