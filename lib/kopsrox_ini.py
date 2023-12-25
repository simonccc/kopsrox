#!/usr/bin/env python3

# generate the default kopsrox.ini
def init_kopsrox_ini():

  # import config parser
  from configparser import ConfigParser

  # get config
  config = ConfigParser(allow_no_value=True)
  config.read('kopsrox.ini')

  # proxmox section
  config.add_section('proxmox')

  # proxmox api endpoint
  config.set('proxmox', '; domain name or IP to access proxmox')
  config.set('proxmox', 'endpoint', '127.0.0.1')
  config.set('proxmox', '; port is usually 8006')
  config.set('proxmox', 'port', '8006')

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

  # kopsrox section
  config.add_section('kopsrox')

  # size for kopsrox nodes
  config.set('kopsrox', 'vm_disk', '20G')

  # number of cpu cores
  config.set('kopsrox', 'vm_cpu', '1')

  # ram size
  config.set('kopsrox', '; amount of ram in Gib ')
  config.set('kopsrox', 'vm_ram', '2')

  # cloudinit user key and password
  config.set('kopsrox', '; username for created cloudinit user')
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

  # cluster section
  config.add_section('cluster')

  # cluster friendly name
  config.set('cluster', '; name for the kopsrox cluster')
  config.set('cluster', 'name', 'mycluster')

  # number of masters
  config.set('cluster', '; number of masters nodes 1 or 3')
  config.set('cluster', 'masters', '1')

  # number of workers
  config.set('cluster', '; number of workers nodes 1 to 5')
  config.set('cluster', 'workers', '0')

  # k3s version
  config.set('cluster', '; k3s version')
  config.set('cluster', 'k3s_version', 'v1.27.8+k3s2')

  # s3 etcd snapshot config
  config.add_section('s3')
  config.set('s3', '; follow your providers details')

  # s3 endpoint
  config.set('s3', 'endpoint', 'kopsrox')
  config.set('s3', '; optional')
  config.set('s3', 'region', '')
  config.set('s3', 'access-key', 'e3898d39d39id93')
  config.set('s3', 'access-secret', 'ioewioeiowe')
  config.set('s3', 'bucket', 'koprox')

  # write config
  # file should not already exist...
  with open('kopsrox.ini', 'w') as configfile:
    config.write(configfile)
  print('created kopsrox.ini please edit')
  return
