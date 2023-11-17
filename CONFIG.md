### [proxmox]

- __endpoint__ = `127.0.0.1` proxmox API host / IP

- __port__ = `8006` port to connect to proxmox API endpoint

- __user__ = `root@pam` - user to connect as

- __token_name__ = `kopsrox` - see api key section above

- __api_key__ = `xxxxxxxxxxxxx` - as generated above

- __proxnode__ = `proxmox` the proxmox node - the image and all nodes are created on this host

- __proxstor__ = `local-lvm` shared storage also works

- __proximgid__ = `600` - the proxmox id used for the kopsrox image/template 

- __up_image_url__ = `https://cloud-images.ubuntu.com/minimal/daily/mantic/current/mantic-minimal-cloudimg-amd64.img` - url to the cloud image you want to use as the base image

- __proxbridge__ = `vmbr0` - the bridge to use - must have internet access

### [kopsrox]

- __vm_disk__ = `20G` - size of the disk for each node in Gigs

- __vm_cpu__ = `1` - number of vcpus for each vm

- __vm_ram__ = amount of ram in G

- __cloudinituser__ = a user account for access to the vm 

- __cloudinitpass__ = password for the user

- __cloudinitsshkey__ = 

- __network__ = "network" address of proxmox cluster

- __networkgw__ = `192.168.0.1` the default gateway for the network ( must provide internet access ) 

- __netmask__ = `24` cdir netmask for the network 

### [cluster]

- __name__ = `kopsrox` name of the cluster

- __k3s_version__ = `v1.24.6+k3s1` 

- __masters__ = `1` number of master nodes - only other supported value is `3`

- __workers__ = `0` number of worker vms eg `1` - values upto `5` are supported

### [s3]

These values are optional 

- __endpoint__ = eg `s3.yourprovider.com`

- __region__ = `optional`

- __access-key__ = `393893894389`

- __access-secret__ = 
