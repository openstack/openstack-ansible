`Home <index.html>`_ OpenStack-Ansible Installation Guide

Running the OpenStack playbook
------------------------------

#. Change to the ``/opt/openstack-ansible/playbooks`` directory.

#. Run the OpenStack setup playbook, which runs a series of
   sub-playbooks:

   .. code-block:: shell-session

       # openstack-ansible setup-openstack.yml

   The openstack-common.yml sub-playbook builds all OpenStack services
   from source and takes up to 30 minutes to complete. As the playbook
   progresses, the quantity of containers in the "polling" state will
   approach zero. If any operations take longer than 30 minutes to
   complete, the playbook will terminate with an error.

   .. code-block:: shell-session

       changed: [target_host_glance_container-f2ebdc06]
       changed: [target_host_heat_engine_container-36022446]
       changed: [target_host_neutron_agents_container-08ec00cd]
       changed: [target_host_heat_apis_container-4e170279]
       changed: [target_host_keystone_container-c6501516]
       changed: [target_host_neutron_server_container-94d370e5]
       changed: [target_host_nova_api_metadata_container-600fe8b3]
       changed: [target_host_nova_compute_container-7af962fe]
       changed: [target_host_cinder_api_container-df5d5929]
       changed: [target_host_cinder_volumes_container-ed58e14c]
       changed: [target_host_horizon_container-e68b4f66]
       <job 802849856578.7262> finished on target_host_heat_engine_container-36022446
       <job 802849856578.7739> finished on target_host_keystone_container-c6501516
       <job 802849856578.7262> finished on target_host_heat_apis_container-4e170279
       <job 802849856578.7359> finished on target_host_cinder_api_container-df5d5929
       <job 802849856578.7386> finished on target_host_cinder_volumes_container-ed58e14c
       <job 802849856578.7886> finished on target_host_horizon_container-e68b4f66
       <job 802849856578.7582> finished on target_host_nova_compute_container-7af962fe
       <job 802849856578.7604> finished on target_host_neutron_agents_container-08ec00cd
       <job 802849856578.7459> finished on target_host_neutron_server_container-94d370e5
       <job 802849856578.7327> finished on target_host_nova_api_metadata_container-600fe8b3
       <job 802849856578.7363> finished on target_host_glance_container-f2ebdc06
       <job 802849856578.7339> polling, 1675s remaining
       <job 802849856578.7338> polling, 1675s remaining
       <job 802849856578.7322> polling, 1675s remaining
       <job 802849856578.7319> polling, 1675s remaining

   Setting up the compute hosts takes up to 30 minutes to complete,
   particularly in environments with many compute hosts. As the playbook
   progresses, the quantity of containers in the "polling" state will
   approach zero. If any operations take longer than 30 minutes to
   complete, the playbook will terminate with an error.

   .. code-block:: shell-session

       ok: [target_host_nova_conductor_container-2b495dc4]
       ok: [target_host_nova_api_metadata_container-600fe8b3]
       ok: [target_host_nova_api_ec2_container-6c928c30]
       ok: [target_host_nova_scheduler_container-c3febca2]
       ok: [target_host_nova_api_os_compute_container-9fa0472b]
       <job 409029926086.9909> finished on target_host_nova_api_os_compute_container-9fa0472b
       <job 409029926086.9890> finished on target_host_nova_api_ec2_container-6c928c30
       <job 409029926086.9910> finished on target_host_nova_conductor_container-2b495dc4
       <job 409029926086.9882> finished on target_host_nova_scheduler_container-c3febca2
       <job 409029926086.9898> finished on target_host_nova_api_metadata_container-600fe8b3
       <job 409029926086.8330> polling, 1775s remaining

   Confirm satisfactory completion with zero items unreachable or
   failed:

   .. code-block:: shell-session

       PLAY RECAP **********************************************************************
       ...
       deployment_host                :  ok=44   changed=11   unreachable=0    failed=0

--------------

.. include:: navigation.txt
