# kopsrox

- cli to automate creating a k3s cluster on proxmox VE using cloud images
- add more master/worker nodes, run kubectl via the cli and a simple config file
- backup  and restore your cluster easily via S3 snapshots
- quick demo: https://asciinema.org/a/597074

## install pre reqs

- `sudo apt install libguestfs-tools -y`

_this is required to patch the cloudimage to install __qemu-guest-agent___

- `pip3 install --break-system-packages --user -r requirements.txt`

_installs the required pip packages vs using os packages_

## [API KEY]

Generate an API key via the command line eg: 

`pvesh create /access/users/root@pam/token/kopsrox`

Take a note of the token as we'll need this below

Set the correct permissions om the token 

`pveum acl modify / --roles Administrator --user root@pam  --token kopsrox`

## kopsrox.ini

Run `./kopsrox.py` and an example kopsrox.ini will be generated

Please edit this file for your setup

### [proxmox]

- __endpoint__ = `localhost` this is where we will connect to proxmox on port 8006

- __user__ = `root@pam` - user

- __token_name__ = `kopsrox` - see [API KEY]

- __api_key__ = as generated above

- __proxnode__ - the proxmox node name where you're running kopsrox from - the image and all nodes are created on this host

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

- __proxbridge__ = `vmbr0` - the proxmox bridge to use for the cluster ( see [kopsrox] section )

### [kopsrox]

- __vm_disk__ = size of the disk in kopsrox vms

- __vm_cpu__ = number ogf vcpus for kopsrox vms

- __vm_ram__ = 

- __cloudinituser__ = 

### [cluster]

- __name__ = name of the cluster

- __k3s_version__ = 

-__masters__ = 

### [s3]

These values are optional see etcd section below

- __endpoint__ = 

- __region__ = 

- __access-key__ = 

# create a cluster
Lets get started by creating a cluster


## create image
To create a kopsrox template run:

`./kopsrox.py create image`

Edit your `kopsrox.ini` and set `masters = 1` in the `[cluster]` section
## create a cluster
`./kopsrox.py cluster create`
- create cluster 
## run kubectl
We can run kubectl via connecting to the master via qagent and running `k3s kubectl`
## add worker
Edit [kopsrox.ini] 
- add worker


# commands
## image
### create
- creates a kopsrox image template
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
### kubectl
- run kubectl 
### kubeconfig
- export the kubeconfig
### destroy
- destroys the cluster
## etcd
- commands to manage s3 snapshots of etcd
### snapshot
### restore
### list
### prune
- deletes old snapshots

# etcd backups guide
- stuff about tokens

## setup
- s3 api

### providers tested
- minio
- cloudflare ( 20G free ) 
- backblaze ( 10 / 75G free )

## snapshot
- takes a snapshot
- check it with ls
## restore
- restoring a cluster
- downsizing
- stuff not working

# FAQ
__can I use debian as a base image vs ubuntu?__

_I had to switch from debian due to some problem with a discovered interface which was dhcp and caused some network problems_

