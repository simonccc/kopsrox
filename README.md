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

You can generate an API key via the command line eg: `pvesh create /access/users/root@pam/token/kopsrox`

Take a note of the token as we'll need this below

Then to set the correct permissions om the token `pveum acl modify / --roles Administrator --user root@pam  --token kopsrox`

## kopsrox.ini

Please edit this file for your setup.. details below:

### proxmox section 

- __endpoint__ ( usually localhost ) this is where we will connect to proxmox on port 8006

- __user__ ( usually root@pam )

- __token_name__  ( default is kopsrox )

- __api_key__   ( as generated above ) 

- __proxnode__ - the proxmox node name where you're running kopsrox from

- __proximgid__ - the "baseid" used within proxmox for proxmox  ( see network and host layout below for more info ) 

### kopsrox section 

#### network and host layout

A kopsrox cluster is made up of upto 3 masters and 5 workers numbered a bit like this

|

- 0. the image
1. master node 1
2. master node 2
3. master node 3
4. spare / unused
5. worker 1
6. worker 2
7. worker 3
8. worker 4
9. worker 5

in the kopsrox.ini you need to define 2 settings that relate to this

- __proximgid__ - this defines the image qemu/proxmox id amd is used as the base for the cluster - so the furst master will be ( proximgid + 1 ) 
   

# commands
## image
- creates a kopsrox image template
## cluster
- creates and updates a cluster
## etcd
- operations eg snapshot / restore
- nodes - delete a node
- config - config operations

# etcd
## setup

To use the etcd snapshot and restore functions you need some s3 compatable storeage

- minio
- backblaze ( 10 / 75G free )

  ## snapshot
  ## restore

# FAQ
__can I use debian as a base image vs ubuntu?__

_I Had to switch from debian due to some problem with it adding another discovered interface which was dhcp and caused some network problems_

