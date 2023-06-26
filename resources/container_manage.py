from flask import jsonify, make_response, request
from flask_restful import Resource, reqparse
from ..config import Config
import os
import shutil
import docker


put_parser = reqparse.RequestParser()
put_parser.add_argument('id', dest='container_id',required=True,help='container id')
put_parser.add_argument('cmd', dest='cmd',required=True,help='container run cmd exec')


del_parser = reqparse.RequestParser()
del_parser.add_argument('path', dest='container_volume_path',required=True,help='container volume path')

post_parser = reqparse.RequestParser()
post_parser.add_argument('image', dest='container_image',required=True,help='container image')
post_parser.add_argument('name', dest='container_name',required=True,help='name of container')
post_parser.add_argument('cpu', dest='cpuset',required=False,help='number of cpu for container')
post_parser.add_argument('mem', dest='memory',required=False,help='memory limit of container')
post_parser.add_argument('env', dest='env',type=dict,required=True,help='container environment varaibles')
post_parser.add_argument('volumes', dest='volumes',type=dict,required=True,help='container volumes')
post_parser.add_argument('ports', dest='ports',type=dict,required=True,help='ports to expose')

class ContainerManager(Resource):
    def get(self,id=None):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            client = docker.from_env()
            if id == None:
                client = docker.from_env()
                containers_list=[]
                for container in client.containers.list():
                    containers_list.append(container.name)
                containers={}
                containers.update({'containers': containers_list})
                return make_response(jsonify(containers),200)
            result = {}
            try:
                container = client.containers.get(id)
            except Exception as e:
                print(e)
                return make_response(jsonify({'result':'getting container status Failed'}),500)
            result.update({'container_spec':{
                'id': f"{container.id}",
                'short_id': f"{container.short_id}",
                'name': f"{container.name}",
                'status': f"{container.status}"
            }})
            return make_response(jsonify(result),200)
            

        return make_response(jsonify({'result':'Not Found(403)'}),403)
        


    def post(self):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            args =  post_parser.parse_args()
            print(args)
            client = docker.from_env()
            volumes = args['volumes']
            ports = args['ports']
            environment = args['env']
            try:
                path = list(volumes.keys())[0]
                if not os.path.exists(path):
                    os.makedirs(path)
                container = client.containers.run(image=f"{args['container_image']}",detach=True,name=f"{args['container_name']}", volumes=volumes,ports=ports,
                        environment=environment,mem_limit=f"{args['memory']}",cpuset_cpus= args['cpuset'])
                container.logs()
                result ={}
                print(container.status)
                if container.status == "exited":
                    return make_response(jsonify({"status":"0","result":"container creating error"}),500)

                else:
                    result.update({'container_spec':{
                        'id': f"{container.id}",
                        'short_id': f"{container.short_id}",
                        'name': f"{container.name}",
                        'status': f"{container.status}"
                    }})
                    result.update({"status":"1","result":"container created"})
                    return make_response(jsonify(result),200)                    
            except Exception as e:
                print('Run container Exception: ',e)
                return make_response(jsonify({'result':'create container error'}),500)

        return make_response(jsonify({'result':'Not Found(403)'}),403)

    def delete(self,id):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            args =  del_parser.parse_args()
            client = docker.from_env()
            try:
                container = client.containers.get(id)
                exit_code = container.remove(v=True, force=True)
                shutil.rmtree(args['container_volume_path'])
                print(exit_code)

                return make_response(jsonify({'status':'1','result':'container removed','message':f"{exit_code}"}),200)
            except Exception as e:
                print("run command error: ",e)
                return make_response(jsonify({'result':'running command error'}),500)

        return make_response(jsonify({'result':'Not Found(403)'}),403)

    def put(self,id):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            args =  put_parser.parse_args()
            print(id,args)
            client = docker.from_env()
            try:
                container = client.containers.get(id)
                exit_code = container.exec_run(cmd=f"{args['cmd']}")
                print(exit_code)
                return make_response(jsonify({'result':'OK'}),200)
            except Exception as e:
                print("run command error: ",e)
                return make_response(jsonify({'result':'running command error'}),500)

        return make_response(jsonify({'result':'Not Found(403)'}),403)

