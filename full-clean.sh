#set -e
echo "removing files"
rm mantic-minimal-cloudimg-amd64.img
rm kopsrox_disk_import.log
rm kopsrox_imgpatch.log
rm kopsrox.k3stoken
rm kopsrox.kubeconfig
echo "kopsrox destroy"
./kopsrox.py cluster destroy
./kopsrox.py image destroy
echo "kopsrox img create"
./kopsrox.py image create
./kopsrox.py image info
echo "kopsrox cluster create"
./kopsrox.py cluster create
./kopsrox.py cluster info
