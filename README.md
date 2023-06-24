# kopsrox
automate creating a k3s cluster with proxmox api with a "kops like" cli

tested with pve 8.0.3

## install

- sudo apt install libguestfs-tools -y
- pip3 install --break-system-packages --user -r requirements.txt
- run ./kopsrox.py
- edit the kopsrox.ini file for your setup

## commands
- image - creates a kopsrox image template
- cluster - creates and updates a cluster
- etcd - etcd operations eg snapshot / restore
- nodes - delete a node
- config - config operations

## in progress
- "utility" node to run minio and other things
