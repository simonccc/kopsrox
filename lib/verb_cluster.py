import common_config as common, sys, os, wget, re, time, urllib.parse
verb = 'cluster'
verbs = common.verbs_cluster

# check for arguments
try:
  if (sys.argv[2]):
    passed_verb = str(sys.argv[2])
except:
  print('ERROR: pass a command')
  print(verb, '', end='')
  common.verbs_help(verbs)
  exit(0)

# unsupported verb
if not passed_verb in verbs:
  print('ERROR:\''+ passed_verb + '\'- command not found')
  print('kopsrox', verb, '', end='')
  common.verbs_help(verbs)

# import config
from configparser import ConfigParser
kopsrox_config = ConfigParser()
import proxmox_config as kprox

# read values from config
kopsrox_config.read(common.kopsrox_conf)

proxnode = kopsrox_config.get('proxmox', 'proxnode')
proxstor = kopsrox_config.get('proxmox', 'proxstor')
proximgid = kopsrox_config.get('proxmox', 'proximgid')
up_image_url = kopsrox_config.get('proxmox', 'up_image_url')
proxbridge = kopsrox_config.get('proxmox', 'proxbridge')

# kopsrox lvl
vm_disk_size = kopsrox_config.get('kopsrox', 'vm_disk_size')
cloudinituser = kopsrox_config.get('kopsrox', 'cloudinituser')
cloudinitsshkey = kopsrox_config.get('kopsrox', 'cloudinitsshkey')
network = kopsrox_config.get('kopsrox', 'network')
networkgw = kopsrox_config.get('kopsrox', 'networkgw')

# generate image name
kopsrox_img = common.kopsrox_img(proxstor,proximgid)

# 
if passed_verb == 'create':
    print('create')
