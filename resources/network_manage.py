from flask import jsonify, make_response, request
from flask_restful import Resource, reqparse
from config import Config
import docker
from common.util import jwt_verified, get_free_ip

post_parser = reqparse.RequestParser()
post_parser.add_argument('name', dest='network_name',required=True,help='name of network')
post_parser.add_argument('subnet', dest='network_subnet',required=True,help='subnet for network')
post_parser.add_argument('gateway', dest='network_gateway',required=False,help='network gateway if need')
post_parser.add_argument('internal', dest='network_internal',required=True,help='docker network internal set')
post_parser.add_argument('driver', dest='network_driver',required=True,help='network driver')

put_parser = reqparse.RequestParser()
put_parser.add_argument('network_name', dest='network_name',required=True,help='name of network')
put_parser.add_argument('container_id', dest='container_id',required=True,help='id of container to connect network')
put_parser.add_argument('container_ipv4', dest='container_ipv4',required=True,help='The IP address of this container on the network')

ip_parser = reqparse.RequestParser()
ip_parser.add_argument('ips', dest='profile_ips',action='append',required=False,help='active profiles ip')
class GetIP(Resource):
    def post(self):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            if jwt_verified(request.headers.get('jwt')):
                try:
                    args = ip_parser.parse_args()
                    free_ip = get_free_ip(profile_ips=args['ips'])
                    if free_ip:
                       return make_response(jsonify({'result':'1','free_ip': f"{free_ip}"}),200)
                    return make_response(jsonify({'result':'0','msg': "free ip error"}),500) 
                except Exception as e:
                    print("free ip Exception:",e)



class NetworkManager(Resource):

    def post(self):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            if jwt_verified(request.headers.get('jwt')):   
                client = docker.from_env()
                args =  post_parser.parse_args()
                network_name = args['network_name']
                network_subnet = args['network_subnet']
                network_gateway = args['network_gateway']
                network_driver = args['network_driver']
                if int(args['network_internal']) == 0:
                    network_internal = False
                else:
                    network_internal = True    
                
                try:
                    ipam_pool = docker.types.IPAMPool(
                        subnet=f"{network_subnet}",
                        gateway=f"{network_gateway}"
                        )
                    ipam_config = docker.types.IPAMConfig(
                        pool_configs=[ipam_pool]
                        )
                    network = client.networks.create(name=network_name,driver=network_driver,internal=network_internal,ipam=ipam_config)
                    result ={}
                    result.update({'id':f"{network.id}",'short_id':f"{network.short_id}",'attrs':f"{network.attrs}",'name':f"{network.name}"})
                    return make_response(jsonify({'result':'1','metadata': f"{result}"}),201)
                except Exception as e:
                    print("run command error: ",e)
                    return make_response(jsonify({'result':'network creation error'}),500)
            return make_response(jsonify({"message":"jwt token not valid"}),401)            
        return make_response(jsonify({'result':'Not Found(403)'}),403)

    def put(self):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            if jwt_verified(request.headers.get('jwt')):   
                client = docker.from_env()
                args =  put_parser.parse_args()
                try:
                    networks = client.networks.list()
                    for net in networks:
                        if net.name == args['network.name']:
                            net.connect(container=args['container_id'],ipv4_address=args['container_ipv4'])
                            return make_response(jsonify({"message":"jwt token not valid"}),401)
                except Exception as e:
                    print("PUt error:",e)
                    return make_response(jsonify({'result':'network update error'}),500)

            return make_response(jsonify({"message":"jwt token not valid"}),401)            

        return make_response(jsonify({'result':'Not Found(403)'}),403) 

    def get(self,id=None):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            if jwt_verified(request.headers.get('jwt')):   
                client = docker.from_env()
                if id == None:
                    try:
                        networks = client.networks.list()
                        docker_networks={}
                        for net in networks:
                                docker_networks.update({"id":f"{net.id}","name":f"{net.name}"})
                        return make_response(jsonify({"result":"1","networks":f"{docker_networks}"}),200)
                    except Exception as e:
                        print("PUt error:",e)
                        return make_response(jsonify({'result':'network update error'}),500)
            return make_response(jsonify({"message":"jwt token not valid"}),401)            
        return make_response(jsonify({'result':'Not Found(403)'}),403)

    def delete(self):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            if jwt_verified(request.headers.get('jwt')):   
                client = docker.from_env()
            return make_response(jsonify({"message":"jwt token not valid"}),401)            

        return make_response(jsonify({'result':'Not Found(403)'}),403)


