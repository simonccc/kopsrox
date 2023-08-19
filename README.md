# kopsrox
automate creating a k3s cluster on proxmox VE

create a cluster, add more nodes, run kubectl and take etcd snapshots quickly with a "kops like" cli using the proxmox api / qaagent

tested with pve 8.0.3 / k3s v1.27.4+k3s1

quick demo: https://asciinema.org/a/597074

# install

- sudo apt install libguestfs-tools -y
- pip3 install --break-system-packages --user -r requirements.txt

# setup
- run ./kopsrox.py a default koprox.ini will be created
## kopsrox.ini
- api key
- network considerations
- run ./kopsrox.py
- edit the kopsrox.ini file for your setup

# commands
- image - creates a kopsrox image template
- cluster - creates and updates a cluster
- etcd - etcd operations eg snapshot / restore
- nodes - delete a node
- config - config operations

# etcd
- s3 service required

# FAQ
__can I use debian as a base image?__
_Had to switch from debian due to some problem with it adding another discovered interface which was dhcp and caused some network problems_

