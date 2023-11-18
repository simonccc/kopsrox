# get started
## create an image

`./kopsrox.py create image`

## create a cluster

`./kopsrox.py cluster create`

## add a worker

Edit `kopsrox.ini` and set `workers = 1` in the `[cluster]` section

`./kopsrox.py cluster update`

## check the cluster info

`./kopsrox.py cluster info`
