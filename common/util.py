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

def get_free_ip(profile_ips=[]):
    import ipaddress
    import os
    try:
        cmd="docker network inspect no-internet | jq -r 'map(.Containers[].IPv4Address) []' | cut -d/ -f1"
        x=os.popen(cmd)
        used_ips = x.read().split()
        subnet =[str(ip) for ip in ipaddress.IPv4Network('172.20.0.0/16')]
        free_list = list(set(used_ips) ^ set(subnet))
        removing_list=['172.20.0.0','172.20.0.1','172.20.0.2','172.20.0.3']
        if profile_ips != None:
            removing_list.extend(profile_ips)
        for i in removing_list:
            if i in free_list:
                free_list.remove(i)
        return free_list.pop(0)
    except Exception as e:
        print("free ip exception:",e)

def get_free_ip_old():
    import docker
    import time
    try:
        client = docker.from_env()
        container = client.containers.run(image=f"nginx",detach=True,name=f"get_free_ip",network_mode='no-internet')
        container_ip = get_container_ips(id=container.id)
        container.remove(force=True,v=True)
        return container_ip[0]
    except Exception as e:
        print("free ip exception:",e)


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
    commands = [
        "bash /.firefox.sh",
        "bash -c 'sed -i 's/novnc2/AqrVdi/g' /usr/local/lib/web/frontend/static/js/app.fef011cae8f5fbff4b55.js ' ",
        "bash -c 'sed -i 's/novnc2/AqrVdi/g' /usr/local/lib/web/frontend/static/js/app.fef011cae8f5fbff4b55.js.map ' ",
        "bash -c 'sed -i 's/novnc2/AqrVdi/g' /usr/local/lib/web/frontend/index.html ' ",
        "bash -c 'apt remove -y lxterminal'",
        "bash -c 'find / -type f -name '.firefox.sh' -exec rm {} \;'",
    ]
    try:
        cmd=f"docker cp /opt/firefox.sh {vd_container_name}:/.firefox.sh"
        os.system(cmd)
        client2 = docker.from_env()
        vd_container = client2.containers.get(container_id=vd_container_name)
        print(vd_container.name)
        for cmd in commands:
            exit_code,output = vd_container.exec_run(cmd=cmd)
            print(cmd,exit_code,output)
    except Exception as e:
        print(e)
    nginx_container_name = f"{Config.NGINX_CONTAINER_NAME}"
    config_path = f"{Config.NGINX_CONFIG_PATH}"
    # nginx_domain = f"{Config.NGINX_DOMAIN}"
    vd_nginx_config = False
    browser_nginx_config = False 
    try:
        config_file = f"{config_path}/conf.d/vdi-proxy.conf"
        # mode = 'a+' if os.path.exists(config_file) else 'w+'
        mode = 'a+'
        #### if config file exists
        if os.path.exists(config_file):
            nginx_config=f"include /etc/nginx/conf.d/{user};" + '\n\n }#[[update]]'
            user_config="""
                location /[[user]] {
                    proxy_pass http://[[container]]/[[user]]/;
                    proxy_http_version 1.1;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection "Upgrade";
                    proxy_set_header Host $host;
                }
                
                location /[[user]]/fbrowser  {
                    proxy_pass http://[[fb_container]];
                    proxy_http_version 1.1;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection "Upgrade";
                    proxy_set_header Host $host;
                }
   
                    """
            if search_and_replace(filename=config_file,old="}#[[update]]",new=nginx_config):
                with open(f"{config_path}/conf.d/{user}", 'w+') as file:
                    file.write(user_config)
                if search_and_replace(filename=f"{config_path}/conf.d/{user}",old="[[user]]",new=f"{user}") and search_and_replace(filename=f"{config_path}/conf.d/{user}",old="[[container]]",new=f"{vd_container_name}") and search_and_replace(filename=f"{config_path}/conf.d/{user}",old="[[fb_container]]",new=f"{browser_container_name}"):
                    client = docker.from_env()
                    container = client.containers.get(container_id=nginx_container_name)
                    exit_code,output = container.exec_run(cmd="nginx -t")
                    if int(exit_code) == 0:
                        exit_code,output = container.exec_run(cmd="nginx -s reload")
                        if int(exit_code) == 0:
                            return True
                        else:
                            print("nginx container not reloaded",output)
                            return False
                    else:
                        print("nginx container config not correct",output)
                        return False
            else: 
                print("search and replace error( include config file")
                return False
            
    except Exception as e:
        print("Exception browser nginx update:",e,repr(e))

        
def nginx_proxy_update_old(user,vd_container_name,browser_container_name):
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
        # mode = 'a+' if os.path.exists(config_file) else 'w+'
        mode = 'a+'
        #### if config file exists
        if os.path.exists(config_file):
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
            if search_and_replace(filename=config_file,old="}#[[update]]",new=append_config) and search_and_replace(filename=config_file,old="[[user]]",new=f"{user}") and search_and_replace(filename=config_file,old="[[container]]",new=f"{vd_container_name}"):
                client = docker.from_env()
                container = client.containers.get(container_id=nginx_container_name)
                exit_code,output = container.exec_run(cmd="nginx -t")
                if int(exit_code) == 0:
                    exit_code,output = container.exec_run(cmd="nginx -s reload")
                    if int(exit_code) == 0:
                        vd_nginx_config = True
                    else:
                        print("nginx container not reloaded",output)
                        vd_nginx_config = False
                else:
                    print("nginx container config not correct",output)
                    vd_nginx_config =  False
            else: 
                print("search and replace error(line123)")
                vd_nginx_config =  False

            
        else:
            with open(config_file, mode) as f:
                f.write(nginx_conf)
            if search_and_replace(filename=config_file,old="[[domain]]",new=f"{nginx_domain}"):

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
                 
            if search_and_replace(filename=config_file,old="}#[[update]]",new=append_config) and search_and_replace(filename=config_file,old="[[container]]",new=f"{vd_container_name}") and search_and_replace(filename=config_file,old="[[user]]",new=f"{user}"):
                client = docker.from_env()
                container = client.containers.get(container_id=nginx_container_name)
                exit_code,output = container.exec_run(cmd="nginx -t")
                if int(exit_code) == 0:
                    exit_code,output = container.exec_run(cmd="nginx -s reload")
                    if int(exit_code) == 0:
                        vd_nginx_config = True
                    else:
                        vd_nginx_config = False
                        print("nginx container not reloaded",output)
                else:
                    vd_nginx_config = False
                    print("nginx container config not correct",output)
            else:
                print("search and replace error(line160)")
                vd_nginx_config = False
        ######## add browser location in nginx            
        if os.path.exists(config_file):
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

            if search_and_replace(filename=config_file,old="}#[[update]]",new=append_config) and search_and_replace(filename=config_file,old="[[user]]",new=f"{user}") and search_and_replace(filename=config_file,old="[[container]]",new=f"{browser_container_name}"):
                client = docker.from_env()
                container = client.containers.get(container_id=nginx_container_name)
                exit_code,output = container.exec_run(cmd="nginx -t")
                if int(exit_code) == 0:
                    exit_code,output = container.exec_run(cmd="nginx -s reload")
                    if int(exit_code) == 0:
                        browser_nginx_config = True
                    else:
                        print("nginx container not reloaded",output)
                        browser_nginx_config = False
                else:
                    print("nginx container config not correct",output)
                    browser_nginx_config =  False
            else:
                print("search and replace error(line197)")
                browser_nginx_config = False
        
    except Exception as e:
        print("Exception browser nginx update:",e)

    if browser_nginx_config and vd_nginx_config:
        return True
    return False
