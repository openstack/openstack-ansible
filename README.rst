Rackspace Private Cloud Version 9.0
###################################
:date: 2014-09-25 09:00
:tags: rackspace, lxc, openstack, cloud, ansible
:category: \*nix

License
-------
Copyright 2014, Rackspace US, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Official Documentation
----------------------

Comprehensive installation guides, including FAQs and release notes, can be found at http://docs.rackspace.com

Playbook Support
----------------

OpenStack:
  * keystone
  * glance-api
  * glance-registry
  * cinder-api
  * cinder-scheduler
  * cinder-volume
  * nova-api
  * nova-api-ec2
  * nova-api-metadata
  * nova-api-os-compute
  * nova-compute
  * nova-conductor
  * nova-scheduler
  * heat-api
  * heat-api-cfn
  * heat-api-cloudwatch
  * heat-engine
  * horizon
  * neutron-server
  * neutron-dhcp-agent
  * neutron-metadata-agent
  * neutron-linuxbridge-agent


Infrastructure:
  * galera
  * rabbitmq
  * logstash
  * elastic-search
  * kibana

Assumptions
-----------

This repo assumes that you have setup the host servers that will be running the OpenStack infrastructure with three
bridged network devices named: ``br-mgmt``, ``br-vxlan``, ``br-vlan``. These bridges will be used throughout
the OpenStack infrastructure.

The repo also relies on configuration files found in the `/etc` directory of this repo.
If you are running Ansible from an "unprivileged" host, you can place the contents of the /etc/ directory in your 
home folder; this would be in a directory similar to `/home/<myusername>/rpc_deploy/`. Once you have the file in place, you
will have to enter the details of your environment in the `rpc_user_config.yml` file; please see the file for how 
this should look. After you have a bridged network and the files/directory in place, continue on to _`Base Usage`.


Base Usage
----------

All commands must be executed from the `rpc_deployment` directory. From this directory you will have access to all
of the playbooks, roles, and variables.  It is recommended that you create an override file to contain any and all 
variables that you wish to override for the deployment. While the override file is is not required it will make life 
a bit easier.

All of the variables that you may wish to update are in the `vars/` directory, however you should also be aware that 
services will pull in base group variables as found in `inventory/group_vars`.

All playbooks exist in the ``playbooks/`` directory and are grouped in different sub-directories.

All of the keys, tokens, and passwords are in the `user_variables.yml` file. This file contains no
preset passwords. To setup your keys, passwords, and tokens you will need to either edit this file
manually or use the script ``pw-token-gen.py``. Example:

.. code-block::

    # Generate the tokens
    scripts/pw-token-gen.py --file /etc/rpc_deploy/user_variables.yml


Example usage from the `rpc_deployment` directory in the `ansible-rpc-lxc` repository

.. code-block:: bash

    # Run setup on all hosts: 
    ansible-playbook -e @vars/user_variables.yml playbooks/setup/host-setup.yml
    
    # Run infrastructure on all hosts
    ansible-playbook -e @vars/user_variables.yml playbooks/infrastructure/infrastructure-setup.yml
    
    # Setup and configure openstack within your spec'd containers
    ansible-playbook -e @vars/user_variables.yml playbooks/openstack/openstack-setup.yml


About Inventory
---------------

All things that Ansible cares about are located in inventory. In the Rackspace Private Cloud all 
inventory is dynamically generated using the previously mentioned configuration files. While this is a dynamically 
generated inventory, it is not 100% generated on every run.  The inventory is saved in a file named 
`rpc_inventory.json` and is located in the directory where you've located your user configuration files. On every 
run a backup of the inventory json file is created in both the current working directory as well as the location where
the user configuration files exist.  The inventory json file is a living document and is intended to grow as the environment 
scales in infrastructure. This means that the inventory file will be appended to as you add more nodes and or change the 
container affinity from within the `rpc_user_config.yml` file. It is recommended that the base inventory file be backed 
up to a safe location upon the completion of a deployment operation. While the dynamic inventory processor has guards in it 
to ensure that the built inventory is not adversely effected by programmatic operations this does not guard against user error
and/or catastrophic failure.


Scaling
-------

If you are scaling the environment using the dynamically generated inventory you should know that the inventory was designed to 
generate new entries in inventory and not remove entries from inventory.  These playbooks will build an environment to spec so if 
container affinity is changed and or a node is added or removed from an environment the user configuration file will need to be 
modified as well as the inventory json.  For this reason it is recommended that should a physical node need replacing it should be 
renamed the same as the previous one. This will make things easier when rebuilding the environment. Additionally if a container
is needing to be replaced it is better to simply remove the misbehaving container and rebuild it using the existing inventory.


Notes
-----

* Library has an experimental `Keystone` module which adds ``keystone:`` support to Ansible. 
* Library has an experimental `Swift` module which adds ``swift:`` support to Ansible.
* Library has an experimental `LXC` module which adds ``lxc:`` support to Ansible. 

