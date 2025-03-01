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
  config.set('proxmox', '; domain or IP to access proxmox')
  config.set('proxmox', 'prox_endpoint', '127.0.0.1')

  # proxmox api port
  config.set('proxmox', '; api port ( usually 8006 ) ')
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
  config.set('proxmox', '; the proxmox node that you will run kopsrox on - the image and all nodes are created on this host')
  config.set('proxmox', 'node', 'proxmox')

  # storage on node
  config.set('proxmox', '; the proxmox storage to use for kopsrox - needs to be available on the proxmox node')
  config.set('proxmox', 'storage', 'local-lvm')

  # kopsrox section
  config.add_section('kopsrox')

  # upstream image
  config.set('kopsrox', '; the upstream cloud image used to create the kopsrox image')
  config.set('kopsrox', 'cloud_image_url', 'https://cloud-images.ubuntu.com/minimal/daily/oracular/current/oracular-minimal-cloudimg-amd64.img')

  # disk size for kopsrox vms
  config.set('kopsrox', '; size of vm disk in Gib ')
  config.set('kopsrox', 'vm_disk', '20')

  # number of cpu cores
  config.set('kopsrox', '; number of cpu cores ')
  config.set('kopsrox', 'vm_cpu', '1')

  # ram size
  config.set('kopsrox', '; amount of ram in Gib ')
  config.set('kopsrox', 'vm_ram', '2')

  # cloudinit user key and password
  config.set('kopsrox', '; username for created cloudinit user')
  config.set('kopsrox', 'cloudinituser', 'user')

  # cloud init user password
  config.set('kopsrox', '; password for the cloudinit user')
  config.set('kopsrox', 'cloudinitpass', 'admin')

  # cloud init user ssh key
  config.set('kopsrox', ';  a ssh public key for the cloudinit user ( required ) ')
  config.set('kopsrox', 'cloudinitsshkey', 'ssh-rsa cioieocieo')

  # network bridge
  config.set('kopsrox', '; network bridge to use with kopsrox')
  config.set('kopsrox', '; a proxmox sdn can be used by specifying the zone and vnet like this: sdn/zone/vnet')
  config.set('kopsrox', 'network_bridge', 'vmbr0')

  # kopsrox network baseip
  config.set('kopsrox', '; first ip of the ip range used for this kopsrox cluster')
  config.set('kopsrox', 'network_ip', '192.168.0.160')

  # netmask / subnet
  config.set('kopsrox', '; /24 is 255.255.255.0')
  config.set('kopsrox', 'network_mask', '24')

  # default gateway
  config.set('kopsrox', '; default gateway for the network ( needs to provide internet access ) ')
  config.set('kopsrox', 'network_gw', '192.168.0.1')

  # dns server
  config.set('kopsrox', '; dns server for network')
  config.set('kopsrox', 'network_dns', '192.168.0.1')

  # network mtu
  config.set('kopsrox', '; interface mtu set on vms ')
  config.set('kopsrox', '; set to 1450 if using sdn ')
  config.set('kopsrox', 'network_mtu', '1500')

  # cluster section
  config.add_section('cluster')

  # cluster vmid
  config.set('cluster', '; id for the cluster vm\'s eg from 620 - 630')
  config.set('cluster', 'cluster_id', '620')

  # cluster friendly name
  config.set('cluster', '; name of the cluster')
  config.set('cluster', 'cluster_name', 'mycluster')

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

  # s3 endpoint
  config.set('s3', '; all s3 settings are optional')
  config.set('s3', '; s3 endpoint')
  config.set('s3', 'endpoint', 'kopsrox')

  # s3 region
  config.set('s3', '; s3 region')
  config.set('s3', 'region', '')

  # s3 access key
  config.set('s3', '; s3 access key')
  config.set('s3', 'access-key', 'e3898d39d39id93')

  # s3 access secret
  config.set('s3', '; s3 access secret')
  config.set('s3', 'access-secret', 'ioewioeiowe')

  # s3 bucket
  config.set('s3', '; s3 bucket')
  config.set('s3', 'bucket', 'koprox')

  # write config
  # file should not already exist...
  with open('kopsrox.ini', 'w') as cfile:
    config.write(cfile)
  print('created kopsrox.ini please edit for your setup')
  return
