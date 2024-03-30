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

  # proxmox api port
  config.set('proxmox', '; port is usually 8006')
  config.set('proxmox', 'port', '8006')

  # username
  config.set('proxmox', '; username to connect with / owner of the API token')
  config.set('proxmox', 'user', 'root@pam')

  # api token name
  config.set('proxmox', '; name of api token')
  config.set('proxmox', 'token_name', 'kopsrox')

  # api key
  config.set('proxmox', '; text of api key')
  config.set('proxmox', 'api_key', 'xxxxxxxxxxxxx')

  # node to operate on
  config.set('proxmox', '; the proxmox node that kopsrox will work on - the image and all nodes are created on this host')
  config.set('proxmox', 'proxnode', 'proxmox')

  # storage on node
  config.set('proxmox', '; the proxmox storage to use for kopsrox - shared storage should work also')
  config.set('proxmox', 'proxstor', 'local-lvm')

  # local image id
  config.set('proxmox', '; the first or base id for the kopsrox vms - this id + 10 is the range used')
  config.set('proxmox', 'proximgid', '600')

  # kopsrox section
  config.add_section('kopsrox')

  # upstream image
  config.set('kopsrox', '; the upstream cloud image used to create the kopsrox template')
  config.set('kopsrox', 'cloud_image_url', 'https://cloud-images.ubuntu.com/minimal/daily/mantic/current/mantic-minimal-cloudimg-amd64.img')

  # disk size for kopsrox vms
  config.set('kopsrox', '; size of kopsrox vm disk in Gib ')
  config.set('kopsrox', 'vm_disk', '20')

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

  # network bridge
  config.set('kopsrox', '; network bridge to use with kopsrox')
  config.set('kopsrox', '; a proxmox sdn can be used by specifying the zone and vnet like this: sdn/zone/vnet')
  config.set('kopsrox', 'network_bridge', 'vmbr0')

  # kopsrox network baseip
  config.set('kopsrox', '; start of ip range used for kopsrox')
  config.set('kopsrox', 'network', '192.168.0.160')

  # netmask / subnet
  config.set('kopsrox', '; /24 is 255.255.255.0')
  config.set('kopsrox', 'netmask', '24')

  # default gateway
  config.set('kopsrox', 'networkgw', '192.168.0.1')

  # dns server
  config.set('kopsrox', 'network_dns', '192.168.0.1')

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

  # s3 region ( optional ) 
  config.set('s3', 'region', '')

  # s3 access key
  config.set('s3', 'access-key', 'e3898d39d39id93')

  # s3 access secret
  config.set('s3', 'access-secret', 'ioewioeiowe')

  # s3 bucket
  config.set('s3', 'bucket', 'koprox')

  # write config
  # file should not already exist...
  with open('kopsrox.ini', 'w') as cfile:
    config.write(cfile)
  print('created kopsrox.ini please edit for your setup')
  return
