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

def search_and_replace(filename, old, new):
    try:
        # Read in the file
        with open(f"{filename}", 'r') as file :
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace(f"{old}", f"{new}")

        # Write the file out again
        with open(f"{filename}", 'w') as file:
            file.write(filedata)
        return True
    except Exception as e:
        print("searchReplace Except:",e)
        return False

def nginx_proxy_update(user,vd_container_name,browser_container_name):
    import os, docker
    nginx_container_name = f"{Config.NGINX_CONTAINER_NAME}"
    config_path = f"{Config.NGINX_CONFIG_PATH}"
    nginx_domain = f"{Config.NGINX_DOMAIN}"
    vd_nginx_config = False
    browser_nginx_config = False
    nginx_conf = """
        server {
            listen 80;
            #listen 443 ssl;

            server_name   [[domain]];

            access_log /var/log/nginx/[[domain]].access.log;
            error_log /var/log/nginx/[[domain]].error.log error;
            
            # ssl_certificate /etc/nginx/ssl/[[domain]]/fullchain.pem;
            # ssl_certificate_key /etc/nginx/ssl/[[domain]]/privkey.pem;
            
            # force https-redirects
            # if ($scheme = http) {
            #     return 301 https://$host$request_uri;
            # }            
        }#[[update]]
      """
    try:
        config_file = f"{config_path}/conf.d/{nginx_domain}.conf"
        mode = 'a+' if os.path.exists(config_file) else 'w+'
        #### if config file exists
        if os.path.exists(config_file):
            if search_and_replace(filename=config_file,old="}#[[update]]",new=""):
                with open(config_file, mode) as f:
                    append_config="""
                        location /[[user]] {
                            proxy_pass http://[[container]]:80/;
                            proxy_http_version 1.1;
                            proxy_set_header Upgrade $http_upgrade;
                            proxy_set_header Connection "Upgrade";
                            proxy_set_header Host $host;
                        }
                        
                    }#[[update]]
                    """
                    f.write(append_config)
                    if search_and_replace(filename=config_file,old="[[user]]",new=f"{user}") and search_and_replace(filename=config_file,old="[[container]]",new=f"{vd_container_name}"):
                        client = docker.from_env()
                        container = client.containers.get(container_id=nginx_container_name)
                        exit_code,output = container.exec_run(cmd="nginx -t")
                        if int(exit_code) == 0:
                            exit_code,output = container.exec_run(cmd="nginx -s reload")
                            if int(exit_code) == 0:
                                vd_nginx_config = True
                            else:
                                print(output)
                                vd_nginx_config = False
                        else:
                            print(output)
                            vd_nginx_config =  False
                    else:
                        print("search and replace error(line125)")
                        vd_nginx_config = False
            else: 
                print("search and replace error(line128)")
                vd_nginx_config =  False

            
        else:
            with open(config_file, mode) as f:
                f.write(nginx_conf)
                if search_and_replace(filename=config_file,old="[[domain]]",new=f"{nginx_domain}") and search_and_replace(filename=config_file,old="}#[[update]]",new=""):

                    append_config="""
                        location /[[user]] {
                            proxy_pass http://[[container]]:80/;
                            proxy_http_version 1.1;
                            proxy_set_header Upgrade $http_upgrade;
                            proxy_set_header Connection "Upgrade";
                            proxy_set_header Host $host;
                        }
                        
                    }#[[update]]
                    """
                    f.write(append_config)
                    if search_and_replace(filename=config_file,old="[[container]]",new=f"{vd_container_name}"):
                        client = docker.from_env()
                        container = client.containers.get(container_id=nginx_container_name)
                        exit_code,output = container.exec_run(cmd="nginx -t")
                        if int(exit_code) == 0:
                            exit_code,output = container.exec_run(cmd="nginx -s reload")
                            if int(exit_code) == 0:
                                vd_nginx_config = True
                            print(output)
                            vd_nginx_config = False
                        print(output)
                        vd_nginx_config = False
                    print("search and replace error(line161)")
                    vd_nginx_config = False               
                else:
                    print("search and replace error(line164)")
                    vd_nginx_config = False
        ######## add browser location in nginx            
        if os.path.exists(config_file):
            if search_and_replace(filename=config_file,old="}#[[update]]",new=""):
                with open(config_file, mode) as f:
                    append_config="""
                        location /[[user]]/browser {
                            proxy_pass http://[[container]]:80/;
                            proxy_http_version 1.1;
                            proxy_set_header Upgrade $http_upgrade;
                            proxy_set_header Connection "Upgrade";
                            proxy_set_header Host $host;
                        }
                        
                    }#[[update]]
                    """
                    f.write(append_config)
                    if search_and_replace(filename=config_file,old="[[user]]",new=f"{user}") and search_and_replace(filename=config_file,old="[[container]]",new=f"{browser_container_name}"):
                        client = docker.from_env()
                        container = client.containers.get(container_id=nginx_container_name)
                        exit_code,output = container.exec_run(cmd="nginx -t")
                        if int(exit_code) == 0:
                            exit_code,output = container.exec_run(cmd="nginx -s reload")
                            if int(exit_code) == 0:
                                browser_nginx_config = True
                            else:
                                print(output)
                                browser_nginx_config = False
                        else:
                            print(output)
                            browser_nginx_config =  False
                    else:
                        print("search and replace error(line197)")
                        browser_nginx_config = False
            else: 
                print("search and replace error(200)")
                browser_nginx_config =  False          
    except Exception as e:
        print("Exception browser nginx update:",e)

    if browser_nginx_config and vd_nginx_config:
        return True
    return False
