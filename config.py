from os import environ
class Config:
    WHITE_LIST_ACCESS_IP = environ.get("VDI_AGENT_WHITELIST_IPS").split(",")