# Config
- [proxmox](#proxmox)
  - [endpoint](#endpoint)
- [kopsrox](#kopsrox)
- [cluster](#cluster)
- [s3](#s3)


## proxmox <a name=proxmox>

### endpoint <a name=endpoint>

`127.0.0.1` proxmox API host / IP

### port

`8006` port to connect to proxmox API endpoint

### user

`root@pam` - user to connect as

### token_name 

`kopsrox` - see api key section above

- __api_key__ = `xxxxxxxxxxxxx` - as generated above

- __proxnode__ = `proxmox` the proxmox node - the image and all nodes are created on this host

- __proxstor__ = `local-lvm` shared storage also works

- __proximgid__ = `600` - the proxmox id used for the kopsrox image/template 

- __up_image_url__ = `https://cloud-images.ubuntu.com/minimal/daily/mantic/current/mantic-minimal-cloudimg-amd64.img` - url to the cloud image you want to use as the base image

- __proxbridge__ = `vmbr0` - the bridge to use - must have internet access

## kopsrox

### vm_disk

`20G` - size of the disk for each node in Gigs

### vm_cpu

`1` - number of vcpus for each vm

### vm_ram

amount of ram in G

### cloudinituser

a user account for access to the vm 

- __cloudinitpass__ = password for the user

- __cloudinitsshkey__ = 

- __network__ = "network" address of proxmox cluster

- __networkgw__ = `192.168.0.1` the default gateway for the network ( must provide internet access ) 

- __netmask__ = `24` cdir netmask for the network 

## cluster <a name=cluster>
### name

`kopsrox` name of the cluster

### k3s_version

`v1.24.6+k3s1` 

### masters

`1` number of master nodes - only other supported value is `3`

- __workers__ = `0` number of worker vms eg `1` - values upto `5` are supported

## s3 <a name=s3>

These values are optional 

### endpoint 

eg `s3.yourprovider.com`

### region

`optional`

- __access-key__ = `393893894389`

- __access-secret__ = 
