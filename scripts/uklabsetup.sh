set -x
LAB=${1:-"uklab16_20"}

function key_create(){
  ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''
}

# Make the system key used for adding to containers
pushd /root/.ssh/
if [ ! -f "id_rsa" ];then
    key_create
fi

if [ ! -f "id_rsa.pub" ];then
  rm "id_rsa"
  key_create
fi

# Install all the things
pushd /root/ansible-lxc-rpc
    # Ensure that the scripts python requirements are installed
    pip install -r requirements.txt
    pushd /root/ansible-lxc-rpc/rpc_deployment
      # Base Setup
      ansible-playbook -e @/etc/rpc_deploy/user_variables.yml playbooks/setup/host-setup.yml

      # Infrastructure Setup
      ansible-playbook -e @/etc/rpc_deploy/user_variables.yml playbooks/infrastructure/infrastructure-setup.yml

      # HAProxy Setup (Only for NON-HW LB, NON Production installs)
      ansible-playbook -e @/etc/rpc_deploy/user_variables.yml playbooks/infrastructure/haproxy-install.yml

      # Openstack Service Setup
      ansible-playbook -e @/etc/rpc_deploy/user_variables.yml playbooks/openstack/openstack-setup.yml

      ansible-playbook -e @/etc/rpc_deploy/user_variables.yml playbooks/openstack/swift-all.yml
    popd
popd
