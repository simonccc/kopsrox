# kopsrox
automate creating a k3s cluster with proxmox api with a "kops like" cli and cluster config files

tested with pve 8.0.3

## install

- sudo apt install libguestfs-tools -y
- pip3 install --break-system-packages --user -r requirements.txt
- run ./kopsrox.py
- update your proxmox.ini and kopsrox.ini configs

## features
- create k3s clusters quickly and easily using proxmox vms
- simple static networking config for vm's based on parameters in config
- snapshot and restore etcd quickly and easily

## commands
- image - creates a kopsrox image template
- cluster - creates and updates a cluster
- etcd - etcd operations eg snapshot / restore
- nodes - delete a node

## in progress
- "utility" node to run minio and other things
- make file get support > 16m ( paused ) 

## problems
- has to run on a proxmox node to run "qm import" 
- needs virt-customize / libguestfs-tools to patch the image for qemu-agent
- user needs sudo qm access
- the api token needs quite high permissions
- no network customisation

## will not support
- multiple clusters
- be able to select which proxmox instance each node gets deployed on
- docker
- network customisation beyond current approach
- private networking
