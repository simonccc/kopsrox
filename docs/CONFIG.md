# kopsrox.ini 

Most values should be obvious and commented in the default kopsrox.ini but some more misc info below


- [proxmox](#proxmox)
  - [proximgid](#proximgid)
- [kopsrox](#kopsrox)
  - [cloud_image_url](#cloud_image_url)
- [cluster](#cluster)
  - [name](#cname)
  - [k3s_version](#k3s_version)
  - [masters](#masters)
  - [workers](#workers)
- [s3](#s3)
  - [endpoint](#s3endpoint)
  - [region](#region)
  - [access-key](#access-key)
  - [access-secret](#access-secret)
  - [bucket](#bucket)

## proxmox <a name=proxmox>

config related to proxmox api level setup 

see [SETUP.md](SETUP.md) for API access details

### proximgid <a name=proximgid>

`600` - the proxmox id used for the kopsrox image/template and the basis of the cluster

kopsrox uses a simple static id/ip assignment scheme based on the `[proxmox] - proximgid` and `[kopsrox] - network` settings 

For example:

```
[proxmox]
proximgid = 620

[kopsrox]
network = 192.168.0.170
```

|-|vmid|ip|type|
|--|--|--|--|
|0|620|-|image|
|1|621|192.168.0.171|master 1|
|2|622|192.168.0.172|master 2|
|3|623|192.168.0.173|master 3|
|4|624|-|spare|
|5|625|192.168.0.175|worker 1|
|6|626|192.168.0.176|worker 2|
|7|627|192.168.0.177|worker 3|
|8|628|192.168.0.178|worker 4|
|9|629|192.168.0.179|worker 5|

See also `[kopsrox]` [network](#network) setting 

## kopsrox

### cloud_image_url <a name=cloud_image_url>

`https://cloud-images.ubuntu.com/minimal/daily/mantic/current/mantic-minimal-cloudimg-amd64.img` 

url to the cloud image you want to use as the koprox base template. 

during `kopsrox.py image create` this is downloaded and patched via `virt-customise` to install `qemu-guest-agent`

qcow images are also supported. 

Tested images so far: 

https://cdn.amazonlinux.com/os-images/2.0.20240306.2/kvm/amzn2-kvm-2.0.20240306.2-x86_64.xfs.gpt.qcow2
https://mirrors.vinters.com/rocky/9/images/x86_64/Rocky-9-GenericCloud.latest.x86_64.qcow2

### network <a name=network>

"network" address of proxmox cluster

`network = 192.168.0.170`

See [proximgid](#proximgid)
