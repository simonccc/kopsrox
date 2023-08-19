# kopsrox
automate creating a k3s cluster on proxmox VE using cloud images

create a cluster, add more nodes, run kubectl and take etcd snapshots quickly with a "kops like" cli

tested with pve 8.0.3 / k3s v1.27.4+k3s1

quick demo: https://asciinema.org/a/597074

# install

You need a running Proxmox VE setup ( cluster or node ) with full root access. 

- `sudo apt install libguestfs-tools -y`

_this is required to patch the cloudimage to install qagent_

- `pip3 install --break-system-packages --user -r requirements.txt`

_installs the required pip packages vs using os packages_

- then run `./kopsrox.py` and a default koprox.ini will be created for you - please edit this file next.
  
## kopsrox.ini

Please edit this file for your setup.. details below:

### proxmox section 

- __endpoint__ ( usually localhost ) this is where we will connect to proxmox on port 8006

- __user__ ( usually root@pam )


###€ API key

You can generate an API key via the command line eg: `pvesh create /access/users/root@pam/token/kopsrox`

- how to set permissions?

- __token_name__  ( default is kopsrox ) 

- __proxnode__ the proxmox node name where you're running kopsrox from

### kopsrox section 
#### network and host layout
- network considerations

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

