import datetime

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from controllers.incident_graph_scheduler import IncidentGraphIntelligenceJob
from models import user
from utils.app_config import config
from utils.common_utils import scheduler
from views import auth_view, alert_view, incident_view, stats_view, callback_view, comment_view, admin, toolkits_view

app = Flask(__name__)
app.config.from_object(__name__)
api = Api(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


app.config['JWT_SECRET_KEY'] = config.get('application.jwt_secret_key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=8)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(minutes=60)

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

api.add_resource(stats_view.AlertCountBySourceView, '/stats/alerts')

api.add_resource(alert_view.AlertView, *['/alerts', '/alerts/<alert_id>'])

api.add_resource(incident_view.IncidentView, '/incidents', '/incidents/<incident_id>')
api.add_resource(incident_view.IncidentView, '/vulnerabilities', '/vulnerabilities/<incident_id>', endpoint='vulnerabilityview')

api.add_resource(incident_view.IncidentRelations, '/incidents/<incident_id>/relations')

api.add_resource(incident_view.IncidentGraphView, '/incidents/<incident_id>/graph')

api.add_resource(comment_view.CommentView, '/comments', '/comments/<event_id>')

api.add_resource(toolkits_view.ToolkitsView, '/toolkits')
api.add_resource(toolkits_view.ToolkitRecordView, '/alerts/<alert_id>/toolkits')

api.add_resource(comment_view.CommentDownloadView, '/comments/<comment_id>/download')

api.add_resource(callback_view.CallbackMessageHandler, '/secmaster/callback')

api.add_resource(admin.SystemInfo, '/system/info')


def _init_scheduler():
    if app.config.get('SCHEDULER_INITIALIZED'):
        return

    app.config.setdefault(
        'SCHEDULER_EXECUTORS',
        {
            'default': {'type': 'threadpool', 'max_workers': 30}
        }
    )
    scheduler.api_enabled = True
    scheduler.init_app(app)
    IncidentGraphIntelligenceJob.register()
    scheduler.start()
    app.config['SCHEDULER_INITIALIZED'] = True


_init_scheduler()


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.run(debug=False, host='0.0.0.0', port=8080)
