#!/usr/bin/env python3
from configparser import ConfigParser

# default ini file name
conf='kopsrox.ini'

# generate the default kopsrox.ini
def init_kopsrox_ini(conf = conf):

  # get config
  config = ConfigParser(allow_no_value=True)
  config.read(conf)

  # proxmox
  config.add_section('proxmox')

  # endpoint
  config.set('proxmox', '; domain name or IP to access proxmox this has to be port 8006 atm')
  config.set('proxmox', 'endpoint', 'domain or ip')

  # username
  config.set('proxmox', '; username in token')
  config.set('proxmox', 'user', 'root@pam')

  # token name
  config.set('proxmox', 'token_name', 'kopsrox')

  # api key
  config.set('proxmox', 'api_key', 'xxxxxxxxxxxxx')

  # node to operate on
  config.set('proxmox', 'proxnode', 'proxmox')

  # storage on node
  config.set('proxmox', 'proxstor', 'local-lvm')

  # local image id
  config.set('proxmox', 'proximgid', '600')

  # upstream image
  config.set('proxmox', 'up_image_url', 'https://cloud-images.ubuntu.com/minimal/daily/mantic/current/mantic-minimal-cloudimg-amd64.img')

  # network bridge
  config.set('proxmox', 'proxbridge', 'vmbr0')

  # kopsrox
  config.add_section('kopsrox')

  # size for kopsrox nodes
  config.set('kopsrox', 'vm_disk', '20G')
  config.set('kopsrox', 'vm_cpu', '1')
  config.set('kopsrox', 'vm_ram', '2')

  # cloudinit user key and password
  config.set('kopsrox', 'cloudinituser', 'user')

  # cloud init user password
  config.set('kopsrox', '; the password for the cloudinit user')
  config.set('kopsrox', 'cloudinitpass', 'admin')

  # cloud init user ssh key
  config.set('kopsrox', 'cloudinitsshkey', 'ssh-rsa cioieocieo')

  # kopsrox network baseip
  config.set('kopsrox', 'network', '192.168.0.160')

  # netmask / subnet
  config.set('kopsrox', '; /24 is 255.255.255.0')
  config.set('kopsrox', 'netmask', '24')

  # default gateway
  config.set('kopsrox', 'networkgw', '192.168.0.1')

  # cluster level
  config.add_section('cluster')
  config.set('cluster', 'name', 'mycluster')
  config.set('cluster', 'masters', '1')
  config.set('cluster', 'workers', '0')

  # k3s version
  config.set('cluster', '; k3s version')
  config.set('cluster', 'k3s_version', 'v1.27.4+k3s1')

  # s3 etcd snapshot config
  config.add_section('s3')
  config.set('s3', 'endpoint', 'kopsrox')
  config.set('s3', '; optional')
  config.set('s3', 'region', '')
  config.set('s3', '; follow your providers details')
  config.set('s3', 'access-key', 'e3898d39d39id93')
  config.set('s3', 'access-secret', 'ioewioeiowe')
  config.set('s3', 'bucket', 'koprox')

  # write config
  # file should not already exist...
  with open(conf, 'w') as configfile:
    config.write(configfile)

  # finished?
  exit(0)
