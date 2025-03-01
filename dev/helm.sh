c=`grep ^cluster_name kopsrox.ini | cut -d ' ' -f3`
helm --kubeconfig=${c}.kubeconfig ${@}
