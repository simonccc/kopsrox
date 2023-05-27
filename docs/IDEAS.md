
## ideas
- could it be a fat command to avoid dependencies and other complications?
- load balancer and bastion support?
- etcd on proxmox volume? can we write to them via api? unlikely

## done
- logs into proxmox via API
- writes init ini files and does some basic checks
- select which node you want to work with and write to config?
- create an image / template for cloning
- create a master node and be able to add workers
- kubectl level support - should export a local kubeconfig
- be able to delete workers safely via cordon and purge
