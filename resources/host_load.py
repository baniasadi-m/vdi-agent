from flask import jsonify, make_response, request
from flask_restful import Resource
from config import Config
import shutil
import os
import psutil
from common.util import jwt_verified

class GetLoad(Resource):
    def get(self):
        if request.remote_addr in Config.WHITE_LIST_ACCESS_IP:
            print(request.headers.get('jwt'))
            if jwt_verified(request.headers.get('jwt')):
                total, used, free = shutil.disk_usage("/")
                free_root_mb = free // (2**20)
                total, used, free = shutil.disk_usage("/home")
                free_home_mb = free // (2**20)
                free_memory_percent = int(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)
                load_avg = os.getloadavg()
                cpu_count = os.cpu_count() 
                
                if int(free_root_mb) > 2000 and int(free_home_mb) > 5000:
                    return make_response(jsonify({'status':'1','load': float(((float(load_avg[2])/float(cpu_count))*200) + (float(free_memory_percent) * 1.5))}),200)
                    
                return make_response(jsonify({'status':'0','load': 10000,'root': free_root_mb,'home':free_home_mb}),200)
            return make_response(jsonify({"message":"jwt token not valid"}),401)
        return make_response(jsonify({"message":"not Found(403)"}),403)