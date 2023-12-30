# kopsrox.ini 
- [proxmox](#proxmox)
  - [endpoint](#endpoint)
  - [port](#port)
  - [user](#user)
  - [token_name](#token_name)
  - [api_key](#api_key)
  - [proxnode](#proxnode)
  - [proxstor](#proxstor)
- [kopsrox](#kopsrox)
  - [vm_disk](#vm_disk)
  - [vm_cpu](#vm_cpu)
  - [vm_ram](#vm_ram)
  - [cloudinituser](#cloudinituser)
  - [cloudinitpass](#cloudinitpass)
- [cluster](#cluster)
  - [name](#cname)
  - [k3s_version](#k3s_version)
  - [masters](#masters)
  - [workers](#workers)
- [s3](#s3)
  - [endpoint](#s3endpoint)
  - [region](#region)
  - [access-key](#access-key)
  - [access-secret](#access-secret)
  - [bucket](#bucket)

## proxmox <a name=proxmox>

config related to proxmox setup 

### endpoint <a name=endpoint>

`127.0.0.1` the proxmox API hostnamei/dns or IP address 

### port <a name=port>

`8006` port to connect to proxmox API endpoint

### user <a name=user>

`root@pam` - user to connect as

### token_name <a name=token_name>

`kopsrox` - see api key section above

### api_key <a name=api_key>

See [SETUP.md](#SETUP.MD)

### proxnode <a name=proxnode>

`proxmox` the proxmox node - the image and all nodes are created on this host

### proxstor <a name=proxstor>

`local-lvm` shared storage also works

### proximgid

`600` - the proxmox id used for the kopsrox image/template 

### up_image_url

`https://cloud-images.ubuntu.com/minimal/daily/mantic/current/mantic-minimal-cloudimg-amd64.img` - url to the cloud image you want to use as the base image

### proxbridge

`vmbr0` - the bridge to use - must have internet access via the `networkgw` defined below

## kopsrox

### vm_disk <a name=vm_disk>

`20G` - size of the disk for each node in Gigs

### vm_cpu <a name=vm_cpu>

`1` - number of vcpus for each vm

### vm_ram <a name=vm_ram>

`2` - amount of ram in G

### cloudinituser <a name=cloudinituser>

a user account for access to the vm 

### cloudinitpass <a name=cloudinitpass>

password for the user

### cloudinitsshkey

`sshkey.pub`

### network

"network" address of proxmox cluster

### networkgw

`192.168.0.1` the default gateway for the network ( must provide internet access ) 

### netmask

 `24` cdir netmask for the network 

## cluster <a name=cluster>

config relating to the cluster

### name <a name=cname>

`kopsrox` name of the cluster

### k3s_version <a name=k3s_version>

`v1.24.6+k3s1` 

### masters <a name=masters>

`1` number of master nodes - only other supported value is `3`

### workers <a name=workers>

`0` number of worker vms eg `1` - values upto `5` are supported

## s3 <a name=s3>

Config for s3 etcd operations. If you're not using this you can leave these blank.

### endpoint <a name=s3endpoint>

eg `s3.yourprovider.com`

### region <a name=region>

`optional`

### access-key <a name=access-key>

`393893894389`

### access-secret <a name=access-secret>

`ioewioeiowe`  - the access secret for your s3 provider

### bucket <a name=bucket>

`kopsrox` - bucket name
