from flask import jsonify, make_response, request
from flask_restful import Resource, reqparse
from config import Config
from common.util import jwt_verified, get_container_ips, get_network_id, nginx_proxy_update

post_parser = reqparse.RequestParser()
post_parser.add_argument('obj', dest='obj',type=dict,required=True,help='which obj updated')

class NginxUpdate(Resource):
    def post(self):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            if jwt_verified(request.headers.get('jwt')):
                args =  post_parser.parse_args()
                if args['obj']['name'] == 'nginx':
                    if nginx_proxy_update(user=args['obj']['user'],vd_container_name=args['obj']['vd_container'],browser_container_name=args['obj']['browser_container']):
                        return make_response(jsonify({"message":"nginx config updated"}),200) 
                    else:
                        return make_response(jsonify({"message":"nginx config failed"}),401)
                return make_response(jsonify({"message":"no object name found"}),401)
            return make_response(jsonify({"message":"jwt token not valid"}),401)            

        return make_response(jsonify({'result':'Not Found(403)'}),403)


                        # if nginx_proxy_update(user=f"{args['container_name']}"):
                        #     result.update({"status":"1","result":"container created"})
                        #     return make_response(jsonify(result),200)  
                        # else:
                        #     print("nginx update error")
                        #     return make_response(jsonify({'result':'nginx update error'}),500) 