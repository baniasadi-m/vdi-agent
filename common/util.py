from config import Config

from jwt import decode
import time


current_time = int(time.time())

secret = Config.JWT_SECRET_KEY

def jwt_verified(token):
    try:
        data = decode(token, secret, Config.JWT_ALGO)
        print(data)
        if data['iss'] == Config.JWT_ISSUER and int(data['exp']) > int(current_time + Config.JWT_EXPIRY_TIME) and int(data['nbf']) > int(current_time - Config.JWT_NOT_BEFORE_TIME):
            return True
    except Exception as e:
        print("jwt verification failed:" ,e)
        return False
    


