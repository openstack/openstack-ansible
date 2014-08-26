set -x

# Install all the things
pushd /root/ansible-lxc-rpc/rpc_deployment
  # Setup the MaaS/Raxmon stuff
  ansible-playbook -e @vars/user_variables.yml playbooks/monitoring/raxmon-setup.yml

  # Setup Local tests
  ansible-playbook -e @vars/user_variables.yml playbooks/monitoring/maas_local.yml

  # Setup Global Tests
  ansible-playbook -e @vars/user_variables.yml playbooks/monitoring/maas_remote.yml

  # Setup Dell OpenManage Tests (Uncomment this if you want to install those monitors)
  ansible-playbook -e @vars/user_variables.yml playbooks/monitoring/maas_dell_hardware.yml
popd
