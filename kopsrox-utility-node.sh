set -e
cd /var/tmp

minio_deb='/var/tmp/minio.deb'
minio_conf='/etc/default/minio'

# check for minio deb and wget if missing
if ! test -f "$minio_deb"; then
  echo "downloading minio deb"
  wget -q https://dl.min.io/server/minio/release/linux-amd64/archive/minio_20230602231726.0.0_amd64.deb -O minio.deb
fi
echo "minio deb exists"

#check if package is installed
if [ $(dpkg-query -W -f='${Status}' minio 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
  echo "installing minio"
  dpkg -i /var/tmp/minio.deb
fi
echo "minio installed"

# add user 
if id minio-user; then
  echo 'minio-user user found'
else
  echo 'minio-user user not found'
  useradd minio-user
  mkdir -p /home/minio-user/.minio/certs
  chown -R minio-user /home/minio-user/
fi

# check minio dir
if ! test -d "/minio"; then
  mkdir /minio
  chown minio-user /minio
fi

#check mini config
if ! test -f "$minio_conf"; then
  echo "writing minio config"
  echo '
MINIO_ACCESS_KEY="minio"
MINIO_VOLUMES="/minio/"
MINIO_OPTS="--address :9000"
MINIO_SECRET_KEY="miniostorage"
' > /etc/default/minio
fi

# look for certgen
if ! test -f "/usr/local/bin/certgen"; then
  echo "getting certgen"
  wget -q https://github.com/minio/certgen/releases/latest/download/certgen-linux-amd64 -O certgen
  chmod +x certgen
  sudo mv certgen /usr/local/bin/certgen
fi
echo "certgen installed"

# look for certs
if ! test -f "/home/minio-user/.minio/certs/public.crt"; then
  echo "no public.crt found"
  cd /home/minio-user/.minio/certs
  certgen -host minio
  chown minio-user * 
  cd /var/tmp
fi
echo "minio cert found"

# check service is running
if systemctl is-active --quiet "minio.service" ; then
  echo "minio already running"
else
  echo "enabling minio "
  systemctl enable minio && systemctl start minio
fi

# check mc installed
if ! test -f "/usr/local/bin/mc"; then
  echo "installing mc"
  wget -q https://dl.min.io/client/mc/release/linux-amd64/mc
  chmod +x mc
  sudo mv mc /usr/local/bin/mc
fi
echo "mc installed"

# set local context
/usr/local/bin/mc --insecure alias set local https://127.0.0.1:9000 minio miniostorage
echo "mc set local"

# create bucket
if ! /usr/local/bin/mc --insecure ls local/kopsrox; then
  echo "mc make bucket"
  /usr/local/bin/mc --insecure mb local/kopsrox
fi
echo "bucket found"
