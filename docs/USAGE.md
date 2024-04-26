#  :hamburger: usage 

- [image](#image)
- [cluster](#cluster)
- [etcd](#etcd)
- [node](#node)
- [k3s](#k3s)

## image <a name=image>
### create 
- deletes any existing template
- downloads the configured cloud image
- installs `qemu-guest-agent` into the image via `virt-customise`
- imports the disk into proxmox storage using a `sudo qm` command
- creates cloudinit drive with cloudinit data
- converts the vm into a template

### update
- an alias for create
  
### destroy 
- :warning: deletes the existing image template
- this is not really required as create deletes any existing image

### info 
- prints info about image/template vm eg storage, id, creation time and source cloud image file
- size
- creation time

## cluster <a name=cluster>
### create 
- creates and updates a cluster - use this to setup a fresh cluster
- if an existing working master is found it runs the same steps as `kopsrox cluster update`
- clones the image to the '-m1' server and configures networking via cloudinit
- exports kubeconfig and node token

### update 
- checks the state of the cluster vs what is configured in `kopsrox.ini`
- adds or deletes workers/masters per `kopsrox.ini`

### info 
- shows a list of ids, hostnames and ips the host they are running on
- shows `kubectl get nodes`

### kubectl 
- provides a quick and basic way to run some kubectl commands for example:

`./kopsrox.py cluster kubectl get events -A`

### destroy 
- :warning: destroys the cluster ( NO WARNING! ) 
- deletes workers then masters in safe order


## :beach_umbrella: k3s <a name=k3s>
### k3stoken 
- exports the clusters k3s token 
- used when restoring from etcd snapshots
### kubeconfig 
- export the cluster kubeconfig to a `$cluster_name.kubeconfig` file 
- file is patched to have correct VIP IP vs 127.0.0.1

## etcd <a name=etcd>
### snapshot 

`./kopsrox.py etcd snapshot`

Takes a backup of etcd

`./kopsrox.py etcd list`

Should show the new backup

### list 

`./kopsrox.py etcd list`

- lists snapshots taken in s3 storage based on cluster name

### restore 

restores a cluster from a snapshot

usage:

`./kopsrox.py etcd restore $imagename`

- :white_check_mark: check you're using the correct k3s token file for the snapshot!

- downsizes the cluster to 1 node then resizes back to the scale set in `kopsrox.ini`

### restore-latest
- restores the cluster from the latest backup in s3

### prune 
- deletes old snapshots per the retention policy set on the bucket

## :bellhop_bell: node <a name=node>

### destroy [hostname]
- :warning: destroys the passed hostname 
### utility
- creates a spare "utility" node -u1

### terminal
- connects you to the passed vms serial console via `qm terminal`

### ssh [hostname] 
- connect via ssh to a kopsrox cluster vm 
- uses configured cloudinit user as username
- requires working ssh key configured in config

### reboot [hostname]
- reboots the host

### k3s-uninstall
- uninstalls k3s using the usual script


