Ansible OpenStack LXC Configuration
===================================
:date: 2013-09-05 09:51
:tags: lxc, openstack, cloud, ansible
:category: \*nix

This directory contains the files needed to make the openstack_deployment process work.
The inventory is generated from a user configuration file named ``openstack_user_config.yml``.
To load inventory you MUST copy the directory ``openstack_deploy`` to either  ``$HOME/`` or ``/etc/``.
With this folder in place, you will need to enter the folder and edit the file ``openstack_user_config.yml``.
The file will contain all of the IP addresses/hostnames that your infrastructure will exist on
as well as a CIDR that your containers will have IP addresses assigned from. This allows for easy 
scaling as new nodes and or affinity for containers is all set within this file. 

Please see the ``openstack_user_config.yml`` file in the provided ``/etc`` directory for more details on how 
that file is setup.

If you need some assistance defining the CIDR for a given ip address range check out http://www.ipaddressguide.com/cidr



Words on openstack_user_config.yml
##################################

While the ``openstack_user_config.yml`` file is noted fairly heavily with examples and information regarding the options, here's some more information on what the file consists of and how to use it.


Global options
--------------

The user configuration file has three globally available options. These options allow you to set the CIDR for all of your containers IP addresses, and a list of used IP addresses that you may not want the inventory system to collide with, global overrides which are added to inventory outside of "group_vars" and "var_files" files.


----

Global Options:
  * cidr:
  * used_ips:
  * global_overrides:

Here's the syntax for ``cidr``.

.. code-block:: yaml
  
  cidr: <string>/<prefix>


----

To tell inventory not to attempt to consume IP addresses which may or may not exist within the defined cidr write all known IP addresses that are already consumed as a list in yaml format.


Heres the ``used_ips`` syntax

.. code-block:: yaml

  used_ips:
    - 10.0.0.250
    - 10.0.0.251
    - 10.0.0.252
    - 10.0.0.253


----

If you want to specify specific globally available options and do not want to place them in ``var_files`` or within the ``group_vars/all.yml`` file you can set them in a key = value par within the ``global_overrides`` hash.

Here's the ``global_overrides`` syntax


.. code-block:: yaml

    global_overrides:
      debug: True
      git_install_branch: master



Predefined host groups
----------------------

The user configuration file has 4 defined groups which have mapping found within the ``openstack_environment.yml`` file. 

The predefined groups are: 
  * infra_hosts: 
  * compute_hosts:
  * storage_hosts:
  * log_hosts:


Any host specified within these groups will have containers built within them automatically. The containers that will be build are all mapped out within the openstack_environment.json file.

When specifying hosts inside of any of the known groups the syntax is as follows: 

.. code-block:: yaml

    infra_hosts:
      infra_host1:
        ip: 10.0.0.1


With this the top key is the host name and ip is used to set the known IP address of the host name. Even if you have the host names set within your environment using either the ``hosts`` file or a resolver you must specify the "ip".

If you want to use a host that is not in a predefined group and is used is some custom out of band Ansible play you can add a top level key for the host type with the host name and "ip" key. The syntax is the exact same as the predefined host groups.


Adding options to containers within targeted hosts
--------------------------------------------------

Within the host variables options can be added that will append to the ``host_vars`` of a given set of containers.  This allows you to add "special" configuration to containers on a targeted host which may come in handy when scaling out or planning a deployment of services.  To add these options to all containers within the host simply add ``container_vars`` under the host name and use ``key: value`` pairs for all of the desired options. All ``key: value`` pairs will be set as ``host_vars`` on all containers found under host name.

Here is an example of turning debug mode on all containers on infra1


.. code-block:: yaml

	infra_hosts:
	  infra1:
	    ip: 10.0.0.10
	    container_vars:
	      debug: True
	  infra2:
	    ...


In this example you can see that we are setting ``container_vars`` under the host name ``infra1`` and that debug was set to True.


Limiting the container types:
    When developing the inventory it may be useful to further limit the containers that will have access to the provided options. In this case you use the option ``limit_container_types`` followed by the type of container you with to limit the options to. When using the ``limit_container_types`` option the inventory script will perform a string match on the container name and if a match is found, even if it's a partial match, the options will be appended to the container.


Here is an example of adding cinder_backends to containers on a host named cinder1 under the ``storage_hosts`` group. The options will be limited to containers matching the type "cinder_volume".


.. code-block:: yaml

	storage_hosts:
	  cinder1:
	    ip: 10.0.0.10
	    container_vars:
	      cinder_backends:
	        limit_container_types: cinder_volume
	        lvm:
	          volume_group: cinder-volumes
	          driver: cinder.volume.drivers.lvm.LVMISCSIDriver
	          backend_name: LVM_iSCSI
	  cinder2:
	    ...
