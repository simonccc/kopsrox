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

## generate a API key

Generate an API key via the command line eg: 

`sudo pvesh create /access/users/root@pam/token/kopsrox`

Take a note of the token as we'll need this below

Set the correct permissions om the token 

`sudo pveum acl modify / --roles Administrator --user root@pam  --token 'root@pam!kopsrox'`

## kopsrox.ini

Run `./kopsrox.py` and an example _kopsrox.ini_ will be generated

Please edit this file for your setup

### [proxmox]

- __endpoint__ = `localhost` this is where we will connect to proxmox on port 8006

- __user__ = `root@pam` - user

- __token_name__ = `kopsrox` - see api key section above

- __api_key__ = as generated above

- __proxnode__ = the proxmox node name where you're running kopsrox from - the image and all nodes are created on this host

- __proximgid__ = the proxmox id used for the kopsrox image/template eg: 170

the other nodes in the cluster use incrementing id's for example with 170:

|id|proximgid|type|                      
|--|--|--|
|0|170|image|
|1|171|master 1|
|2|172|master 2|
|3|173|master 3|
|4|174|spare|
|5|175|worker 1|
|6|176|worker 2|
|7|177|worker 3|
|8|178|worker 4|
|9|179|worker 5|

- __up_image_url__ = `https://cloud-images.ubuntu.com/minimal/daily/mantic/current/mantic-minimal-cloudimg-amd64.img` - url to the cloud image you want to use

- __proxbridge__ = `vmbr0` - the proxmox bridge to use for koprox

### kopsrox

- __vm_disk__ = size of the disk in kopsrox vms

- __vm_cpu__ = number of vcpus for kopsrox vms

- __vm_ram__ = amount of ram eg 2g

- __cloudinituser__ = 

- __cloudinitpass__ = 

- __cloudinitsshkey__ = 

- __network__ = "network address of proxmox cluster

### cluster

- __name__ = `kopsrox` name of the cluster

- __k3s_version__ = `v1.24.6+k3s1` 

- __masters__ = `1` or `3` - number of masters

- __workers__ = `0` number of worker vms eg 1

### s3

These values are optional 

- __endpoint__ = eg `s3.yourprovider.com`

- __region__ = 

- __access-key__ = 

- __access-secret__ = 

# create  cluster

Lets get started by creating a cluster


## create image
To create a kopsrox template run:

`./kopsrox.py create image`

This will download the img file patch it and create a template to create vms

* path to iso is in koprox.ini


## create a cluster
Edit your `kopsrox.ini` and set `masters = 1` in the `[cluster]` section

`./kopsrox.py cluster create`

This will create a single node cluster

## run kubectl
We can run kubectl via connecting to the master via qagent and running `k3s kubectl`

`./kopsrox.py cluster kubectl get pods -A`

## add worker
Edit [kopsrox.ini] 
- add worker - set `workers = 1` in the `[cluster]` section then run

`./kopsrox.py cluster update`


`./kopsrox.py cluster info`


# commands
## image
### create
- creates a kopsrox image template
- downloads cloud image
- patches it
### destroy
- deletes the existing image template
delete the .img file manually if you want a fresh download
## cluster
- manage the kopsrox cluster
### create
- creates and updates a cluster
### update
- updates cluster state per config
### info
- displays cluster info
-- shows a list of vms, ids, hostnames and ips
-- shows kubectl get nodes
### kubectl
- run kubectl commands
### kubeconfig
- export the kubeconfig
### destroy
- destroys the cluster
## etcd
- commands to manage s3 snapshots of etcd
### snapshot
- create a etcd snapshot in the configured S3 storage
### restore
- restores cluster from etcd backup - requires a image name 
### list
- lists snapshots taken in s3 storage
### prune
- deletes old snapshots

# etcd backups guide

The first time a snapshot is taken a token is written into the kopsrox directory

- `kopsrox.etcd.snapshot.token`

## setup
Kopsrox uses the k3s built in commands to backup to s3 api compatible storage

### providers tested
- minio
- cloudflare ( 20G free ) 
- backblaze ( 10G free )

## snapshot
- takes a snapshot
`./kopsrox.py etcd snapshot`
- check it with ls
## restore
- restoring a cluster
- downsizing
- stuff not working

# FAQ
__can I use debian as a base image vs ubuntu?__

_I had to switch from debian due to some problem with a discovered interface which was dhcp and caused some network problems_

