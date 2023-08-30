from flask import Flask, Blueprint
from flask_restful import Api
from resources.host_load import GetLoad
from resources.container_manage import ContainerManager
from resources.network_manage import NetworkManager
from resources.get_ip import GetIP
from resources.nginx_manage import NginxUpdate
from resources.squid_manage import SquidUpdate


app = Flask(__name__)
api_bp = Blueprint("apiv1_bp",__name__,url_prefix="/api/v1")
api = Api(api_bp)

api.add_resource(GetLoad, '/load')
api.add_resource(ContainerManager, '/containers','/containers/<id>')
api.add_resource(NetworkManager, '/networks')
api.add_resource(NginxUpdate, '/nginxupdate')
api.add_resource(SquidUpdate, '/squidupdate')
api.add_resource(GetIP, '/getip')
app.register_blueprint(api_bp)