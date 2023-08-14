from flask import jsonify, make_response, request
from flask_restful import Resource, reqparse
from config import Config
import os
import shutil
import docker
from common.util import jwt_verified, get_container_ips, get_network_id


put_parser = reqparse.RequestParser()
put_parser.add_argument('id', dest='container_id',required=True,help='container id')
put_parser.add_argument('cmd', dest='cmd',required=True,help='container run cmd exec')


del_parser = reqparse.RequestParser()
del_parser.add_argument('path', dest='container_volume_path',action='append',required=False,help='container volume path')
del_parser.add_argument('ids', dest='container_ids',action='append',required=False,help='container volume path')

post_parser = reqparse.RequestParser()
post_parser.add_argument('image', dest='container_image',required=True,help='container image')
post_parser.add_argument('name', dest='container_name',required=True,help='name of container')
post_parser.add_argument('cpu', dest='cpuset',required=False,help='number of cpu for container')
post_parser.add_argument('mem', dest='memory',required=False,help='memory limit of container')
post_parser.add_argument('env', dest='env',type=dict,required=True,help='container environment varaibles')
post_parser.add_argument('volumes', dest='volumes',type=dict,required=True,help='container volumes')
# post_parser.add_argument('ports', dest='ports',action='append',required=True,help='ports to expose')
post_parser.add_argument('ip', dest='ip',required=False,help='ip to set')
post_parser.add_argument('network', dest='network',required=True,help='network name')

import socket


def get_free_port(port=30000, max_port=40000 ):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while port <= max_port:
        try:
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            port += 1
    raise IOError('no free ports')

class ContainerManager(Resource):
    def get(self,id=None):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            if jwt_verified(request.headers.get('jwt')):   
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
                    return make_response(jsonify({'status':'0','result':'getting container status Failed'}),500)
                container_ips = get_container_ips(id=f"{container.id}")
                result.update({'status':'1','container_spec':{
                    'id': f"{container.id}",
                    'short_id': f"{container.short_id}",
                    'name': f"{container.name}",
                    'status': f"{container.status}",
                    'ips': f"{container_ips}"
                }})
                return make_response(jsonify(result),200)
            return make_response(jsonify({"message":"jwt token not valid"}),401)            

        return make_response(jsonify({'result':'Not Found(403)'}),403)
        


    def post(self):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            if jwt_verified(request.headers.get('jwt')): 
                args =  post_parser.parse_args()
                # print(args)
                client = docker.from_env()
                volumes = args['volumes']
                # ports = {}
                # ports.update({f"80/tcp"})
                # return_ports=[]
                # for port in args['ports']:
                    # host_free_port = get_free_port()
                    # ports.update({f"{port}/tcp":int(f"{host_free_port}")})
                    # return_ports.append(host_free_port)
                    # ports.update({f"{port}/tcp"})
                # print(ports)
                environment = args['env']
                try:
                    path = list(volumes.keys())[0]
                    if not os.path.exists(path):
                        os.makedirs(path)
                    container = client.containers.run(image=f"{args['container_image']}",detach=True,name=f"{args['container_name']}", volumes=volumes,
                            environment=environment,mem_limit=f"{args['memory']}",cpuset_cpus= args['cpuset'],network_mode='temp0')
                    
                    #    container = client.containers.run(image=f"{args['container_image']}",detach=True,name=f"{args['container_name']}", volumes=volumes,ports=ports,
                    #         environment=environment,mem_limit=f"{args['memory']}",cpuset_cpus= args['cpuset'],network_mode='none')
                                     
                    container.logs()
                    result ={}
                    # print(container.status)
                    if container.status == "exited":
                        return make_response(jsonify({"status":"0","result":"container creating error"}),500)

                    else:
                        temp_net_id = get_network_id(name='temp0')
                        temp_net_obj = client.networks.get(network_id=temp_net_id)
                        net_id = get_network_id(name=args['network'])
                        net_obj = client.networks.get(network_id=net_id)
                        if f"{args['ip']}":
                            net_obj.connect(container=f"{container.id}",ipv4_address=f"{args['ip']}")
                            temp_net_obj.disconnect(container=f"{container.id}")
                        else:
                            net_obj.connect(container=f"{container.id}")
                            temp_net_obj.disconnect(container=f"{container.id}")
                        container_ips = get_container_ips(id=f"{container.id}")
                        result.update({'container_spec':{
                            'id': f"{container.id}",
                            'short_id': f"{container.short_id}",
                            'name': f"{container.name}",
                            'status': f"{container.status}",
                            'ips':f"{container_ips}"
                        }})
                        result.update({"status":"1","result":"container created"})
                        return make_response(jsonify(result),200)                    
                except Exception as e:
                    print('Run container Exception: ',e)
                    container.remove(force=True,v=True)
                    return make_response(jsonify({"status":"0",'result':'create container error'}),500)
            return make_response(jsonify({"message":"jwt token not valid"}),401)

        return make_response(jsonify({'result':'Not Found(403)'}),403)

    def delete(self):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            if jwt_verified(request.headers.get('jwt')):
                args =  del_parser.parse_args()
                client = docker.from_env()
                try:
                    for cid in args['container_ids']:
                        container = client.containers.get(cid)
                        exit_code = container.remove(v=True, force=True)
                    for dirpath in args['container_volume_path']:
                        shutil.rmtree(dirpath)
                        return make_response(jsonify({'status':'1','result':'containers removed','message':f"{exit_code}"}),200)
                except Exception as e:
                    print("run command error: ",e)   
            return make_response(jsonify({"message":"jwt token not valid"}),401)             

        return make_response(jsonify({'result':'Not Found(403)'}),403)

    def put(self,id):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            if jwt_verified(request.headers.get('jwt')):
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
            return make_response(jsonify({"message":"jwt token not valid"}),401) 

        return make_response(jsonify({'result':'Not Found(403)'}),403)

