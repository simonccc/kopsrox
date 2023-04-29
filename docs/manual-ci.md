#https://cdimage.debian.org/images/cloud/buster/latest/debian-10-
generic-amd64.qcow2
img=debian-10-generic-amd64.qcow2
storage=lenny_data
#wget https://cloud-images.ubuntu.com/hirsute/current/${img}
qm destroy 9000
qm create 9000 --memory 2048 --net0 virtio,bridge=vmbr0
qm importdisk 9000 ${img} ${storage}
qm set 9000 --scsihw virtio-scsi-pci --scsi0 ${storage}:vm-9000-d
isk-0
qm set 9000 --ide2 ${storage}:cloudinit
qm set 9000 --name k3s-deb
#qm set 8000 --boot order=scsi0
qm set 9000 --boot c --bootdisk scsi0
