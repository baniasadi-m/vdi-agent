from flask import jsonify, make_response, request
from flask_restful import Resource, reqparse
from config import Config
import docker
from common.util import jwt_verified, get_free_ip

parser = reqparse.RequestParser()
parser.add_argument('ips', dest='profile_ips',action="append",required=False,help='active profiles ip')

class GetIP(Resource):
    def post(self):

        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:            
            if jwt_verified(request.headers.get('jwt')):
                try:
                    args = parser.parse_args()
                    print(args)
                    free_ip = get_free_ip(profile_ips=args['profile_ips'])
                    if free_ip:
                       return make_response(jsonify({'result':'1','free_ip': f"{free_ip}"}),200)
                    return make_response(jsonify({'result':'0','msg': "free ip error"}),500) 
                except Exception as e:
                    print("free ip Exception:",e)

