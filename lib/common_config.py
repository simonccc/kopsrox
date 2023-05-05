# upstream image
up_image_url = 'https://cdimage.debian.org/images/cloud/bullseye/latest/debian-11-generic-amd64.qcow2'

# defines
kopsrox_prompt='kopsrox:'
proxmox_conf='proxmox.ini'
kopsrox_conf='kopsrox.ini'

# verbs
top_verbs = ['image', 'cluster']
verbs_image = ['info', 'create']
verbs_cluster = ['info', 'create']

import urllib3, sys
from configparser import ConfigParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from proxmoxer import ProxmoxAPI

# print passed verbs
def verbs_help(verbs):
  print('commands:', '\n')
  for i in verbs:
    print(i)

# generating the proxmox kopsrox image name
def kopsrox_img(proxstor,proximgid):
    return(proxstor + ':base-' + proximgid + '-disk-0')

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

# clone
def clone(vmid):

    # read config
    config = read_kopsrox_ini2()
    proxnode = (config['proxmox']['proxnode'])
    proxstor = (config['proxmox']['proxstor'])
    proximgid = (config['proxmox']['proximgid'])

    # map network info
    network = (config['kopsrox']['network'])
    networkgw = (config['kopsrox']['networkgw'])

    # defaults
    hostname = 'unknown'
    ip = network

    # map hostname
    if ( int(vmid) == ( int(proximgid) + 1 )):
      hostname = 'kopsrox-m1'

    # get ip
    network_octs = network.split('.')
    basenetwork = ( network_octs[0] + '.' + network_octs[1] + '.' + network_octs[2] + '.' ) 
    ip = basenetwork + str(int(network_octs[-1]) + ( int(vmid) - int(proximgid)))

    # init proxmox
    prox = prox_init()
   
    # clone
    print('creating vm', vmid, hostname)
    clone = prox.nodes(proxnode).qemu(proximgid).clone.post(
            newid = vmid,
            name = hostname,
            )
    task_status(prox, clone, proxnode)
    print('done creating vm', vmid)

    # cloudinit
    cloudinit = prox.nodes(proxnode).qemu(vmid).config.post(
                ipconfig0 = ( 'gw=' + networkgw + ',ip=' + ip + '/32' ))
    task_status(prox, str(cloudinit), proxnode)
    print('set ip', ip)

# returns a dict of all config
def read_kopsrox_ini2():
  kopsrox_config = ConfigParser()
  kopsrox_config.read(kopsrox_conf)
  return({s:dict(kopsrox_config.items(s)) for s in kopsrox_config.sections()})

# return kopsrox config
def read_kopsrox_ini():
  kopsrox_config = ConfigParser()
  kopsrox_config.read(kopsrox_conf)

  proxnode = kopsrox_config.get('proxmox', 'proxnode')
  proxstor = kopsrox_config.get('proxmox', 'proxstor')
  proximgid = kopsrox_config.get('proxmox', 'proximgid')
  up_image_url = kopsrox_config.get('proxmox', 'up_image_url')
  proxbridge = kopsrox_config.get('proxmox', 'proxbridge')
  vm_disk_size = kopsrox_config.get('kopsrox', 'vm_disk_size')
  cloudinituser = kopsrox_config.get('kopsrox', 'cloudinituser')
  cloudinitsshkey = kopsrox_config.get('kopsrox', 'cloudinitsshkey')
  network = kopsrox_config.get('kopsrox', 'network')
  networkgw = kopsrox_config.get('kopsrox', 'networkgw')

  # return
  return(proxnode,proxstor,proximgid,up_image_url,proxbridge,vm_disk_size,cloudinituser,cloudinitsshkey,network,networkgw)

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
  # network bridge
  kopsrox_config.set('proxmox', 'proxbridge', 'vmbr0')

  # kopsrox config
  kopsrox_config.add_section('kopsrox')
  # disk size for kopsrox nodes
  kopsrox_config.set('kopsrox', 'vm_disk_size', '40G')
  # cloudinit user and key
  kopsrox_config.set('kopsrox', 'cloudinituser', 'user')
  kopsrox_config.set('kopsrox', 'cloudinitsshkey', 'ssh-rsa cioieocieo')
  # kopsrox network baseip
  kopsrox_config.set('kopsrox', 'network', '192.168.0.160')
  kopsrox_config.set('kopsrox', 'networkgw', '192.168.0.1')
  # cluster level
  kopsrox_config.add_section('cluster')
  kopsrox_config.set('cluster', 'masters', '1')
  kopsrox_config.set('cluster', 'workers', '0')

  # write default config
  with open(kopsrox_conf, 'w') as configfile:
    kopsrox_config.write(configfile)
  print('NOTE: please edit', kopsrox_conf, 'as required for your setup')
  exit(0)

# generate a default proxmox.ini
def init_proxmox_ini():
  conf = proxmox_conf
  proxmox_config = ConfigParser()
  proxmox_config.read(conf)
  proxmox_config.add_section('proxmox')
  # need to add port in the future
  proxmox_config.set('proxmox', 'endpoint', 'domain or ip')
  proxmox_config.set('proxmox', 'user', 'root@pam')
  proxmox_config.set('proxmox', 'token_name', 'token name')
  proxmox_config.set('proxmox', 'api_key', 'xxxxxxxxxxxxx')
  # write file
  with open(conf, 'w') as configfile:
    proxmox_config.write(configfile)
  print('NOTE: please edit', conf, 'as required for your setup')
  exit(0)

# task blocker
def task_status(proxmox_api, task_id, node_name):
    data = {"status": ""}
    while (data["status"] != "stopped"):
      data = proxmox_api.nodes(node_name).tasks(task_id).status.get()
    #print('d', data)
