# upstream image
up_image_url = 'https://cdimage.debian.org/images/cloud/bullseye/latest/debian-11-generic-amd64.qcow2'

# defines
kopsrox_prompt='kopsrox:'
proxmox_conf='proxmox.ini'
kopsrox_conf='kopsrox.ini'

# verbs
top_verbs = ['image']
verbs_image = ['list', 'create']

import urllib3, sys
from configparser import ConfigParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from proxmoxer import ProxmoxAPI

# print passed verbs
def verbs_help(verbs):
  print('commands:', '\n')
  for i in verbs:
    print(i)

def kopsrox_img(proxstor,proximgid):
    return(proxstor + ':vm-' + proximgid + '-disk-0')

# config checker
def conf_check(config,section,value,filename):
  try:
    return(config.get(section, value))
  except:
    print('ERROR: no value found for ' + section + ':' + value + ' in ' + filename)
    exit(0)

# connect to proxmox
def prox_init():

  # read proxmox config
  proxmox_config = ConfigParser()
  proxmox_config.read(proxmox_conf)

  # check values in config
  endpoint = conf_check(proxmox_config,'proxmox','endpoint',proxmox_conf)
  user = conf_check(proxmox_config,'proxmox','user',proxmox_conf)
  token_name = conf_check(proxmox_config,'proxmox','token_name',proxmox_conf)
  api_key = conf_check(proxmox_config,'proxmox','api_key',proxmox_conf)

  prox = ProxmoxAPI(
endpoint,
user=user,
token_name=token_name,
token_value=api_key,
verify_ssl=False,
timeout=10)

  return prox

# generate the default kopsrox.ini
def init_kopsrox_ini():
  kopsrox_config = ConfigParser()
  kopsrox_config.read(kopsrox_conf)
  # create sections
  kopsrox_config.add_section('proxmox')
  # node to operate on
  kopsrox_config.set('proxmox', 'proxnode', 'proxmox')
  # storage on node
  kopsrox_config.set('proxmox', 'proxstor', 'local-lvm')
  # local image id
  kopsrox_config.set('proxmox', 'proximgid', '600')
  # upstream image
  kopsrox_config.set('proxmox', 'up_image_url', up_image_url)
  # write default config
  with open(kopsrox_conf, 'w') as configfile:
    kopsrox_config.write(configfile)
  print('NOTE: please edit', kopsrox_conf, 'as required for your setup')
  exit(0)
