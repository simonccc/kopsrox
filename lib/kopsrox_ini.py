import common_config as common
from configparser import ConfigParser

# generate the default kopsrox.ini
def init_kopsrox_ini():

  # get config
  kopsrox_config = ConfigParser()
  kopsrox_config.read(common.kopsrox_conf)

  # create sections
  kopsrox_config.add_section('proxmox')
  # node to operate on
  kopsrox_config.set('proxmox', 'proxnode', 'proxmox')
  # storage on node
  kopsrox_config.set('proxmox', 'proxstor', 'local-lvm')
  # local image id
  kopsrox_config.set('proxmox', 'proximgid', '600')
  # upstream image
  kopsrox_config.set('proxmox', 'up_image_url', 'https://cloud-images.ubuntu.com/minimal/daily/mantic/current/mantic-minimal-cloudimg-amd64.img')
  # network bridge
  kopsrox_config.set('proxmox', 'proxbridge', 'vmbr0')

  # kopsrox config
  kopsrox_config.add_section('kopsrox')

  # size for kopsrox nodes
  kopsrox_config.set('kopsrox', 'vm_disk', '20G')
  kopsrox_config.set('kopsrox', 'vm_cpu', '1')
  kopsrox_config.set('kopsrox', 'vm_ram', '4')

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
  kopsrox_config.set('cluster', 'k3s-version', 'v1.24.6+k3s1')

  # write default config
  with open(common.kopsrox_conf, 'w') as configfile:
    kopsrox_config.write(configfile)
  print('NOTE: please edit', common.kopsrox_conf, 'as required for your setup')
  exit(0)

# generate a default proxmox.ini
def init_proxmox_ini():

  # proxmox conf
  conf = common.proxmox_conf
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
