from flask import jsonify, make_response, request
from  flask_restful import Resource

import docker

class ContainerManager(Resource):
    def get(self):
        # source_addr = get_remote_addr(request)
        # source_addr = '127.0.0.1'
        # if source_addr in WHITE_LIST_IP:
        if True:
            client = docker.from_env()
            containers=[]
            for container in client.containers.list():
                containers.append(container.name)
            x={}
            x.update({'containers':f"{containers}"})
            print(containers)
            return make_response(jsonify(x,200))


    def post(self):
        pass
