# kopsrox
automate creating a k3s cluster with proxmox api with a "kops like" cli and cluster config files

## install
- sudo apt install libguestfs-tools -y
- pip3 install --user -r requirements.txt
- run ./proxmox.py

## commands
- image - creates a kopsrox image / displays when it was created
- cluster - creates and updates a cluster
- etcd - etcd operations eg snapshot / restore
- nodes - delete a node

## in progress
- make file get support > 16m

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
