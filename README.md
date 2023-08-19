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
- run ./kopsrox.py a default and koprox.ini will be created
  
## kopsrox.ini

Please edit this file for your setup as below:

- __endpoint__ ( usually localhost ) this is where we will connect to proxmox 
- how to generate api key can it be done with pvesh?
- proxnode
- network considerations

# commands
## image
- creates a kopsrox image template
## cluster
- creates and updates a cluster
- etcd - etcd operations eg snapshot / restore
- nodes - delete a node
- config - config operations

# etcd

To use the etcd snapshot and restore functions you need some 
- s3 service required

# FAQ
__can I use debian as a base image vs ubuntu?__

_I Had to switch from debian due to some problem with it adding another discovered interface which was dhcp and caused some network problems_

