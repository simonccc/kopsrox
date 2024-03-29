# kopsrox.ini 
- [proxmox](#proxmox)
  - [endpoint](#endpoint)
  - [port](#port)
  - [user](#user)
  - [token_name](#token_name)
  - [api_key](#api_key)
  - [proxnode](#proxnode)
  - [proxstor](#proxstor)
  - [proximgid](#proximgid)
  - [up_image_url](#up_image_url)
  - [proxbridge](#proxbridge)
- [kopsrox](#kopsrox)
  - [vm_disk](#vm_disk)
  - [vm_cpu](#vm_cpu)
  - [vm_ram](#vm_ram)
  - [cloudinituser](#cloudinituser)
  - [cloudinitpass](#cloudinitpass)
  - [cloudinitsshkey](#cloudinitsshkey)
  - [network](#network)
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

see [SETUP.md](SETUP.md) for API access details

### endpoint <a name=endpoint>

`127.0.0.1` the proxmox API hostnamei/dns or IP address 

127.0.0.1 will work on any host running proxmox

### port <a name=port>

`8006` port to connect to proxmox API endpoint

8006 is the default 

### user <a name=user>

user to connect to proxmox API as 

default is `root@pam`


### token_name <a name=token_name>

`kopsrox` 

### api_key <a name=api_key>

`icjecjeijciejceinceini` 

### proxnode <a name=proxnode>

`proxmox` the proxmox node that kopsrox will work on - the image and all nodes are created on this host

### proxstor <a name=proxstor>

`local-lvm` shared storage also works

### proximgid <a name=proximgid>

`600` - the proxmox id used for the kopsrox image/template and the basis of the cluster

kopsrox uses a simple static id/ip assignment scheme based on the `[proxmox] - proximgid` and `[kopsrox] - network` settings 

For example:

```
[proxmox]
proximgid = 620

[kopsrox]
network = 192.168.0.170
```

|-|vmid|ip|type|
|--|--|--|--|
|0|620|-|image|
|1|621|192.168.0.171|master 1|
|2|622|192.168.0.172|master 2|
|3|623|192.168.0.173|master 3|
|4|624|-|spare|
|5|625|192.168.0.175|worker 1|
|6|626|192.168.0.176|worker 2|
|7|627|192.168.0.177|worker 3|
|8|628|192.168.0.178|worker 4|
|9|629|192.168.0.179|worker 5|

See also `[kopsrox]` [network](#network) setting 

### up_image_url <a name=up_image_url>

`https://cloud-images.ubuntu.com/minimal/daily/mantic/current/mantic-minimal-cloudimg-amd64.img` 

url to the cloud image you want to use as the koprox base template. 

during `kopsrox.py image create` this is downloaded and patched via `virt-customise` to install `qemu-guest-agent`

qcow images are also supported. 

Tested images so far: 

https://cdn.amazonlinux.com/os-images/2.0.20240306.2/kvm/amzn2-kvm-2.0.20240306.2-x86_64.xfs.gpt.qcow2
https://mirrors.vinters.com/rocky/9/images/x86_64/Rocky-9-GenericCloud.latest.x86_64.qcow2


### proxbridge <a name=proxbridge>

`vmbr0` - the bridge to use - must have internet access via the [networkgw](#networkgw) defined below

a proxmox sdn can be used by specifying the zone and vnet like this: `sdn/zone/vnet`

## kopsrox

### vm_disk <a name=vm_disk>

`20G` - size of the disk for each node in Gigs

### vm_cpu <a name=vm_cpu>

`1` - number of vcpus for each vm

### vm_ram <a name=vm_ram>

`2` - amount of ram in G

### cloudinituser <a name=cloudinituser>

`admin` - a user account for access to the vm 

you can use this user name / password to login on the vm if required

### cloudinitpass <a name=cloudinitpass>

`password` - a password for the `cloudinituser` - you can use this user name / password to login on the vm if required

### cloudinitsshkey <a name=cloudinitsshkey>

`sshkey.pub`

### network <a name=network>

"network" address of proxmox cluster

`network = 192.168.0.170`

See [proximgid](#proximgid)

### networkgw

`192.168.0.1` the default gateway for the network ( must provide internet access ) 

### netmask

 `24` cdir netmask for the network 

This is equal to '255.255.255.0' 

## cluster <a name=cluster>

config relating to the cluster

### name <a name=cname>

`kopsrox` name of the cluster

the name is displayed in the cli output

nodes are named eg kopsrox-m1

### k3s_version <a name=k3s_version>

`v1.24.6+k3s1` - the version of k3s installed

### masters <a name=masters>

`1` number of master nodes - only other supported value is `3`

### workers <a name=workers>

`0` number of worker nodes in the cluster - values upto `5` are supported

## s3 <a name=s3>

config values for s3 etcd snapshot/restore operations. 

If you're not using this you can leave these blank.

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
