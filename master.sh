ssh-keygen -f "/home/simonc/.ssh/known_hosts" -R "192.168.0.161"
ping -c 3 192.168.0.161
ssh 192.168.0.161
