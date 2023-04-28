import urllib3, sys
from configparser import ConfigParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from proxmoxer import ProxmoxAPI

# defines
kopsrox_prompt='kopsrox:'
proxmox_conf='proxmox.ini'

# connect to proxmox
def prox_init():

  proxmox_config = ConfigParser()
  proxmox_config.read(proxmox_conf)
  endpoint = proxmox_config.get('proxmox', 'endpoint')
  user = proxmox_config.get('proxmox', 'user')
  token_name = proxmox_config.get('proxmox', 'token_name')
  api_key = proxmox_config.get('proxmox', 'api_key')

  prox = ProxmoxAPI(
endpoint,
user=user,
token_name=token_name,
token_value=api_key,
verify_ssl=False,
timeout=10)

  return prox
