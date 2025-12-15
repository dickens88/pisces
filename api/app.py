import datetime

from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from flask_restful import Api

from controllers.incident_graph_scheduler import IncidentGraphIntelligenceJob
from models import user
from utils.app_config import config
from utils.auth_util import parse_w3_token, TokenCache
from utils.common_utils import scheduler
from utils.logger_init import logger
from views import auth_view, alert_view, incident_view, stats_view, callback_view, comment_view, admin, toolkits_view, ai_prompt_view

app = Flask(__name__)
app.config.from_object(__name__)
api = Api(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

app.config['JWT_SECRET_KEY'] = config.get('application.auth.jwt_secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=8)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(minutes=60)

jwt = JWTManager(app)
app.config['JWT_BLOCKLIST_TOKEN_CHECKS'] = ['access']


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, decrypted_token):
    jti = decrypted_token['jti']
    return user.RevokedTokenModel.is_jti_blacklisted(jti)


@app.after_request
def after_request(response):
    client_ip = request.headers.get("X-Real-IP", request.remote_addr)
    try:
        if config.get("application.auth.method", "jwt") == "jwt":
            verify_jwt_in_request(optional=True)
            username = get_jwt_identity() or 'anonymous'
        else:
            cached_user = TokenCache().get_token(token=parse_w3_token(request))
            username = cached_user.get("cn", "anonymous") if cached_user else 'anonymous'
    except Exception as e:
        username = 'anonymous'

    logger.info(
        f'{client_ip} - - url="{request.method} {request.url}",user_agent="{request.headers.get("User-Agent", "-")}",'
        f'status={response.status_code},length={request.content_length},user="{username}"'
    )
    
    return response


# for user login api
api.add_resource(auth_view.UserLogin, '/login')
api.add_resource(auth_view.UserLogoutAccess, '/logout')
api.add_resource(auth_view.UserRefresh, '/refresh')
api.add_resource(auth_view.UserView, '/user/password')
api.add_resource(auth_view.UserManagement, '/user/management')
api.add_resource(auth_view.LoginRestToken, '/login/rest/token')

# for alert and incident handling api
api.add_resource(stats_view.AlertCountBySourceView, '/stats/alerts')

api.add_resource(alert_view.AlertView, *['/alerts', '/alerts/<alert_id>'])

api.add_resource(incident_view.IncidentView, '/incidents', '/incidents/<incident_id>')
api.add_resource(incident_view.IncidentView, '/vulnerabilities', '/vulnerabilities/<incident_id>', endpoint='vulnerabilityview')

api.add_resource(incident_view.IncidentRelations, '/incidents/<incident_id>/relations')

api.add_resource(incident_view.IncidentGraphView, '/incidents/<incident_id>/graph')

api.add_resource(comment_view.CommentView, '/comments', '/comments/<event_id>')

api.add_resource(toolkits_view.ToolkitsView, '/toolkits')
api.add_resource(toolkits_view.ToolkitRecordView, '/toolkits/records')
api.add_resource(ai_prompt_view.AIPromptView, '/ai/prompt')

api.add_resource(comment_view.CommentDownloadView, '/comments/<comment_id>/download')

# for ASM functions api

# for system common functions
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

