# downloads image for use with serve.sh
if [ ! -f "noble-server-cloudimg-amd64.img" ] 
then
wget "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"
fi 

# untested
if [ ! -f amzn2-kvm-2.0.20240306.2-x86_64.xfs.gpt.qcow2 ] 
then
wget https://cdn.amazonlinux.com/os-images/2.0.20240306.2/kvm/amzn2-kvm-2.0.20240306.2-x86_64.xfs.gpt.qcow2
fi
#if [ ! -f Rocky-9-GenericCloud.latest.x86_64.qcow2 ] 
#then
#wget https://mirrors.vinters.com/rocky/9/images/x86_64/Rocky-9-GenericCloud.latest.x86_64.qcow2
#fi
