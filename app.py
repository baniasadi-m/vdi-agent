from flask import Flask, Blueprint
from flask_restful import Api
from .resources.host_load import GetLoad
from .resources.container_manage import ContainerManager


app = Flask(__name__)
api_bp = Blueprint("apiv1_bp",__name__,url_prefix="/api/v1")
api = Api(api_bp)

api.add_resource(GetLoad, '/load')
api.add_resource(ContainerManager, '/container')
app.register_blueprint(api_bp)