import datetime

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from models import user
from utils.common_utils import generate_random_string
from views import auth_view, alert_view, incident_view, stats_view, callback_view, comment_view
from views import mock_dashboard_view

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

api.add_resource(stats_view.AlertCountBySourceView, '/api/stats/alerts')

api.add_resource(callback_view.CallbackMessageHandler, '/api/secmaster/callback')

api.add_resource(alert_view.AlertView, *['/api/alerts', '/api/alerts/<alert_id>'])

api.add_resource(incident_view.IncidentView, '/api/incidents', '/api/incidents/<incident_id>')

api.add_resource(incident_view.IncidentRelations, '/api/incidents/<incident_id>/relations')

api.add_resource(comment_view.CommentView, '/api/comments', '/api/comments/<comment_id>')

# Mock API路由 - 仪表板相关
api.add_resource(mock_dashboard_view.MockDashboardStatisticsView, '/api/dashboard/statistics')
api.add_resource(mock_dashboard_view.MockRecentOpenAlertsView, '/api/dashboard/recent-alerts')
api.add_resource(mock_dashboard_view.MockRecentOpenVulnerabilitiesView, '/api/dashboard/recent-vulnerabilities')


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['SCHEDULER_EXECUTORS'] = {
        'default': {'type': 'threadpool', 'max_workers': 30}
    }
    # scheduler.api_enabled = True
    # scheduler.init_app(app)
    # scheduler.start()

    app.run(debug=False, host='0.0.0.0', port=8080)
