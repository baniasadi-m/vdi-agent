from config import Config

from jwt import decode
import time


current_time = int(time.time())

secret = Config.JWT_SECRET_KEY
jwt_options = {
   'verify_signature': False,
}
def jwt_verified(token):
    try:
        data = decode(jwt=token, key=secret,options=jwt_options,algorithms=[Config.JWT_ALGO])
        print(data)
        if data['iss'] == Config.JWT_ISSUER and int(data['exp']) > int(current_time + Config.JWT_EXPIRY_TIME) and int(data['nbf']) > int(current_time - Config.JWT_NOT_BEFORE_TIME):
            return True
    except Exception as e:
        print("jwt verification failed:" ,e)
        return False
    
def get_container_ips(id):
    import docker
    try:
        client = docker.from_env()
        container = client.containers.get(id)
        networks = container.attrs.get("NetworkSettings").get("Networks")
        list_ips = []
        for k,v in networks.items():
            print(container.attrs['NetworkSettings']['Networks'][k]['IPAddress'])
            list_ips.append(container.attrs['NetworkSettings']['Networks'][k]['IPAddress'])
    except Exception as e:
        print("list ips exception:",e)
    return list_ips   

def get_network_id(name):
    import docker
    try:
        client = docker.from_env()
        networks = client.networks.list()
        for net in networks:
            if net.name == name:
                return net.id
    except Exception as e:
        print("get net id exception:",e)
