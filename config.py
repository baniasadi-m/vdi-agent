from os import environ
class Config:
    WHITE_LIST_ACCESS_IP = environ.get("VDI_AGENT_WHITELIST_IPS").split(",")
    JWT_SECRET_KEY = environ.get("VDI_AGENT_JWT_SECRET_KEY")
    JWT_ALGO = environ.get("VDI_AGENT_JWT_ALGO","HS512")
    JWT_EXPIRY_TIME = int(environ.get("VDI_AGENT_JWT_EXPIRY_TIME","60"))
    JWT_NOT_BEFORE_TIME = int(environ.get("VDI_AGENT_JWT_NOT_BEFORE_TIME","3600"))
    JWT_ISSUE_AT = int(environ.get("VDI_AGENT_JWT_ISSUE_AT","60"))
    JWT_ISSUER = environ.get("VDI_AGENT_JWT_ISSUER")
    NGINX_CONTAINER_NAME = environ.get("VDI_AGENT_NGINX_CONTAINER_NAME")
    NGINX_CONFIG_PATH = environ.get("VDI_AGENT_NGINX_CONFIG_PATH")
    NGINX_DOMAIN = environ.get("VDI_AGENT_NGINX_DOMAIN")
