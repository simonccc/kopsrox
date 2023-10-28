# kopsrox

- cli to automate creating a k3s cluster on proxmox VE using cloud images
- add more master/worker nodes using simple config file
- backup and restore your cluster easily via S3 snapshots
- quick demo: https://asciinema.org/a/597074

## setup prerequisites

- `sudo apt install libguestfs-tools -y`

_this is required to patch the cloudimage to install qemu-guest-agent_

- `pip3 install --break-system-packages --user -r requirements.txt`

_installs the required pip packages vs using os packages_

## Proxmox API key

Generate an API key via the command line eg: 

`sudo pvesh create /access/users/root@pam/token/kopsrox`

Take a note of the token as we'll need this below

Set the correct permissions om the token 

`sudo pveum acl modify / --roles Administrator --user root@pam  --token 'root@pam!kopsrox'`

## kopsrox.ini

Run `./kopsrox.py` and an example _kopsrox.ini_ will be generated

Please edit this file for your setup

### proxmox

- __endpoint__ = `127.0.0.1` proxmox API host / IP

- __port__ = `8006` port to connect to proxmox API endpoint

- __user__ = `root@pam` - user to connect as

- __token_name__ = `kopsrox` - see api key section above

- __api_key__ = `xxxxxxxxxxxxx` - as generated above

- __proxnode__ = `proxmox` the proxmox node name where you're running kopsrox from - the image and all nodes are created on this host

- __proxstor__ = `local-lvm`

- __proximgid__ = `600` - the proxmox id used for the kopsrox image/template 

the other nodes in the cluster use incrementing id's for example with `proximgid` = 170:

|id|proximgid|type|                      
|--|--|--|
|0|170|image|
|1|171|master 1|
|2|172|master 2|
|3|173|master 3|
|4|--|spare|
|5|175|worker 1|
|6|176|worker 2|
|7|177|worker 3|
|8|178|worker 4|
|9|179|worker 5|

- __up_image_url__ = `https://cloud-images.ubuntu.com/minimal/daily/mantic/current/mantic-minimal-cloudimg-amd64.img` - url to the cloud image you want to use as the base image

- __proxbridge__ = `vmbr0` - the bridge to use - must have internet access

### kopsrox

- __vm_disk__ = size of the disk for each node in Gigs

- __vm_cpu__ = number of vcpus for each vm

- __vm_ram__ = amount of ram in G

- __cloudinituser__ = a user account for access to the vm 

- __cloudinitpass__ = password for the user

- __cloudinitsshkey__ = 

- __network__ = "network" address of proxmox cluster

the nodes in the cluster use incrementing ip 's for example with 192.168.0.170 as the network address

|id|proximgid|ip|type|
|--|--|--|--|
|0|170|-|image|
|1|171|192.168.0.171|master 1|
|2|172|192.168.0.172|master 2|
|3|173|192.168.0.173|master 3|
|4|174|-|spare|
|5|175|192.168.0.175|worker 1|
|6|176|192.168.0.176|worker 2|
|7|177|192.168.0.177|worker 3|
|8|178|192.168.0.178|worker 4|
|9|179|192.168.0.179|worker 5|

- __networkgw__ = 

- __netmask__ = `24` cdir netmask for the network 


### cluster

- __name__ = `kopsrox` name of the cluster

- __k3s_version__ = `v1.24.6+k3s1` 

- __masters__ = `1` number of master nodes - only other supported value is `3`

- __workers__ = `0` number of worker vms eg `1` - values upto `5` are supported

### s3

These values are optional 

- __endpoint__ = eg `s3.yourprovider.com`

- __region__ = `optional`

- __access-key__ = `393893894389`

- __access-secret__ = 

# get started
## create image
To create a kopsrox template run:

`./kopsrox.py create image`

This will download the img file patch it and create a template to create vms

downloads the image file defined in `koprox.ini` as `up_image_url` under the `[proxmox]` section

## create a cluster
Edit `kopsrox.ini` and set `masters = 1` in the `[cluster]` section

`./kopsrox.py cluster create`

This will create a single node cluster

## run kubectl

`./kopsrox.py cluster kubectl get pods -A`

## add worker

Edit `kopsrox.ini` and set `workers = 1` in the `[cluster]` section

`./kopsrox.py cluster update`

the worker will be created and added to the cluster

`./kopsrox.py cluster info`

displays the new cluster state

# commands
## image
### create
- creates a kopsrox image template with proxmox id xxx
- downloads cloud image
- patches it ( installs packages qagent + nfs client) 
- installs k3s 
### destroy
- deletes the existing image template
- delete the .img file manually if you want a fresh download
## cluster
### create
- creates and updates a cluster - use this to setup a fresh cluster
- checks for existing master and then runs update
### update
- updates cluster state per config
- adds or deletes nodes
### info
- displays cluster info
-- shows a list of vms, ids, hostnames and ips
-- shows kubectl get nodes
### kubectl
- run kubectl commands
### kubeconfig
- export the kubeconfig to `kopsrox.kubeconfig` file and patches IP to be masters IP
### destroy
- destroys the cluster ( NO WARNING! ) 
## etcd
### snapshot
- create a etcd snapshot in the configured S3 storage
### restore
- restores cluster from etcd backup - requires a image name which can be got with the list command
- downsizes the cluster to 1 node 
### list
- lists snapshots taken in s3 storage based on cluster name
### prune
- deletes old snapshots by 7 days? ( tbc ) 

# etcd backups guide

The first time a snapshot is taken the cluster token is written into the kopsrox directory

- `kopsrox.etcd.snapshot.token`

This is not overwritten

## setup
kopsrox uses the k3s built in commands to backup to s3 api compatible storage via logging into the master via qagent 

### providers tested
- minio ( selfhosted ) 
- cloudflare ( 20G free ) 
- backblaze ( 10G free )

## snapshot
take a snapshot

`./kopsrox.py etcd snapshot`

`./kopsrox.py etcd list `

## restore

`./kopsrox.py etcd list`

lists snapshost
check you're using the correct key

`./kopsrox.py etcd restore $imagenname`

`./kopsrox.py etcd restore kopsrox-kopsrox-m1-1696692280

etcd::restore: downsizing cluster for restore

etcd::restore: restoring kopsrox-kopsrox-m1-1696692280

proxmox:writefile: kopsrox-m1:/var/tmp/kopsrox.etcd.snapshot.token

etcd::restore: restoring please wait`

- downsizes to 1 node
- stuff not working
-- leaves old nodes behind

# FAQ
__can I use debian as a base image vs ubuntu?__

_I had to switch from debian due to some problem with a discovered interface which was dhcp and caused some network problems_

__k3s_mon 30 second timeouts?__

_Check network settings - the vms can't connect to the internet

