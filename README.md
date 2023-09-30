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

## API key

generate an API key via the command line eg: 

`pvesh create /access/users/root@pam/token/kopsrox`

Take a note of the token as we'll need this below

Set the correct permissions om the token 

`pveum acl modify / --roles Administrator --user root@pam  --token kopsrox`

## kopsrox.ini

Run `./kopsrox.py` and an example kopsrox.ini will be generated

Please edit this file for your setup

### [proxmox]

- __endpoint__ ( usually localhost ) this is where we will connect to proxmox on port 8006

- __user__ ( usually root@pam )

- __token_name__  ( default is kopsrox )

- __api_key__ = as generated above

- __proxnode__ - the proxmox node name where you're running kopsrox from - the image and all nodes are created on this host

- __proximgid__ - the proxmox id used for the kopsrox image/template eg: 170

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

- __up_image_url__ = the url to the cloud image you want to use

- __proxbridge__ = the proxmox bridge to use for the cluster eg vmbr0

### [kopsrox]

- __vm_disk__ = size of the disk in kopsrox vms

- __vm_cpu__ = 

### [cluster]

- __name__ =

### s3 section 

- __endpoint__ = 

# getting started
## create image
- create image
- set masters=1
## create a cluster
- create cluster 
## add worker
- add worker
## etcd operations
- s3 guide
- create
- list
- restore

# commands
## image
### create
- creates a kopsrox image template
### destroy
## cluster
- manage the kopsrox cluster
### create
- creates and updates a cluster
### update
## etcd
### snapshot
### restore
- operations eg snapshot / restore
- nodes - delete a node
- config - config operations

# etcd backups guide
## setup

- minio
- cloudflare ( 20G free ) 
- backblaze ( 10 / 75G free )

  ## snapshot
  ## restore

# FAQ
__can I use debian as a base image vs ubuntu?__

_I had to switch from debian due to some problem with a discovered interface which was dhcp and caused some network problems_

