#!/usr/bin/env python3
from configparser import ConfigParser

# ini file names
conf='kopsrox.ini'

# generate the default kopsrox.ini
def init_kopsrox_ini():

  # get config
  config = ConfigParser()
  config.read(conf)

  # proxmox
  config.add_section('proxmox')

  # endpoint
  config.set('proxmox', 'endpoint', 'domain or ip')

  # username
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

  # cloudinit user and key
  config.set('kopsrox', 'cloudinituser', 'user')
  config.set('kopsrox', 'cloudinitsshkey', 'ssh-rsa cioieocieo')

  # kopsrox network baseip
  config.set('kopsrox', 'network', '192.168.0.160')
  config.set('kopsrox', 'networkgw', '192.168.0.1')

  # cluster level
  config.add_section('cluster')
  config.set('cluster', 'masters', '1')
  config.set('cluster', 'workers', '0')
  config.set('cluster', 'k3s-version', 'v1.24.6+k3s1')

  # write default config
  with open(conf, 'w') as configfile:
    config.write(configfile)
  print('NOTE: please edit', conf, 'as required for your setup')
  exit(0)
