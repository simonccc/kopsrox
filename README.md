# kopsrox
automate creating a k3s cluster with proxmox api with a "kops like" cli

tested with pve 8.0.3

Quick demo: https://asciinema.org/a/597074


# requirements
- proxmox server/cluster
- 1G disk space

## install

- sudo apt install libguestfs-tools -y
- pip3 install --break-system-packages --user -r requirements.txt

# setup
- what a kopsrox cluster needs
-- api key
-- disk space
-- network considerations
- run ./kopsrox.py
- edit the kopsrox.ini file for your setup

## commands
- image - creates a kopsrox image template
- cluster - creates and updates a cluster
- etcd - etcd operations eg snapshot / restore
- nodes - delete a node
- config - config operations
