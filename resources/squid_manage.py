from flask import jsonify, make_response, request
from flask_restful import Resource, reqparse
from config import Config
from common.util import jwt_verified
import docker

post_parser = reqparse.RequestParser()
post_parser.add_argument('username', dest='username',required=True,help='local user in squid')
post_parser.add_argument('password', dest='password',required=True,help='local password in squid')

class SquidUpdate(Resource):
    def post(self):
        print(post_parser.parse_args())
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            if jwt_verified(request.headers.get('jwt')):
                args =  post_parser.parse_args()
                print(args)
                client = docker.from_env()
                squid_container = client.containers.get(container_id='squid-proxy')
                cmd = f"bash -c 'echo {args['username']}:{args['password']} >> /passwords.local'"
                try:
                    exit_code,output = squid_container.exec_run(cmd=cmd,detach=True)
                    print(cmd,exit_code,output)
                    if exit_code == 0:
                        cmd = f"bash -c '/usr/sbin/squid -k reconfigure'"
                        exit_code,output = squid_container.exec_run(cmd=cmd,detach=True)
                        return make_response(jsonify({"status":"1","message":"user created"}),201)
                    return make_response(jsonify({"status":"0","message":"user creating failed"}),501)

                except Exception as e:
                    print(e)
                    return make_response(jsonify({"status":"0","message":"user creating failed"}),501)
            return make_response(jsonify({"message":"jwt token not valid"}),401)            

        return make_response(jsonify({'result':'Not Found(403)'}),403)
    
    def delete(self):
        print(post_parser.parse_args())
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            if jwt_verified(request.headers.get('jwt')):
                args =  post_parser.parse_args()
                print(args)
                client = docker.from_env()
                squid_container = client.containers.get(container_id='squid-proxy')
                cmd = f"bash -c 'sed -i  '/{args['username']}:{args['password']}/d' /passwords.local'"
                try:
                    exit_code,output = squid_container.exec_run(cmd=cmd)
                    print(cmd,exit_code,output)
                    if int(exit_code) == 0:
                        cmd = f"bash -c '/usr/sbin/squid -k reconfigure'"
                        print(cmd)
                        exit_code,output = squid_container.exec_run(cmd=cmd)
                        return make_response(jsonify({"status":"1","message":"user created"}),201)
                    return make_response(jsonify({"status":"0","message":"user creating failed"}),501)
                except Exception as e:
                    print(e)
                    return make_response(jsonify({"status":"0","message":"user creating failed"}),501)
            return make_response(jsonify({"message":"jwt token not valid"}),401)            
        return make_response(jsonify({'result':'Not Found(403)'}),403)