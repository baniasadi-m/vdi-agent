from flask import jsonify, make_response, request
from  flask_restful import Resource
import shutil
import os
import psutil

class GetLoad(Resource):
    def get(self):
        # source_addr = get_remote_addr(request)
        # source_addr = '127.0.0.1'
        # if source_addr in WHITE_LIST_IP:
        if True:
            total, used, free = shutil.disk_usage("/")
            free_root_mb = free // (2**20)
            total, used, free = shutil.disk_usage("/home")
            free_home_mb = free // (2**20)
            free_memory_percent = int(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)
            load_avg = os.getloadavg()
            cpu_count = os.cpu_count() 
            
            if int(free_root_mb) > 2000 and int(free_home_mb) > 5000:
                return make_response(jsonify({'load': float(((float(load_avg[2])/float(cpu_count))*200) + (float(free_memory_percent) * 1.5))}),200)
                
            return make_response(jsonify({'load': 10000,'root': free_root_mb,'home':free_home_mb}),200)
        return make_response(jsonify({"message":"not Found(403)"}),403)