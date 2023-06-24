from flask import jsonify, make_response, request
from flask_restful import Resource
from ..config import Config

import docker

class ContainerManager(Resource):
    def get(self):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            client = docker.from_env()
            containers_list=[]
            for container in client.containers.list():
                containers_list.append(container.name)
            containers={}
            containers.update({'containers': containers_list})
            return make_response(jsonify(containers),200)
        return make_response(jsonify({'result':'Not Found(403)'}),403)
        


    def post(self):
        pass