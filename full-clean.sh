set -x
set -e
echo "kopsrox destroy"
./kopsrox.py cluster destroy
./kopsrox.py image destroy
echo "kopsrox img create"
./kopsrox.py image create
./kopsrox.py image info
echo "kopsrox cluster create"
./kopsrox.py cluster create
./kopsrox.py cluster info
