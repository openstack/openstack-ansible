Upgrade playbooks
=================

This section describes the playbooks that are used in the upgrade process in
further detail.

Within the main :file:`scripts` directory there is an :file:`upgrade-utilities`
directory, which contains an additional playbooks directory. These playbooks
facilitate the upgrade process.


cinder-adjustments.yml
----------------------

This playbook searches for **udev dev devtmpfs** entries in cinder-volume
container configuration files. It then corrects and removes duplicate entries
as needed.


container-network-adjustments.yml
---------------------------------

This playbook logs into the containers throughout the deployment and removes
the Juno network interface files in :file:`interface.d` directory. These
files are removed because the layout and syntax changed in the community
release of OpenStack Ansible, and if present during the upgrade process,
they may cause interface or IP conflicts within the container infrastructures.


container-network-bounce.yml
----------------------------

This playbook logs into the containers and restarts all networks that have an
interface file in the :file:`interfaces.d` directory.


horizon-adjustments.yml
-----------------------

This playbook corrects several user and group permissions in Horizon
containers, preventing permission issues with existing data.


host-adjustments.yml
--------------------

This playbook corrects container configuration files removing items conflicting
with the upgrade and redeployment process. This playbook also iterates through
and fixes log locations that may be locked or otherwise located in the wrong
place.


keystone-adjustments.yml
------------------------

This playbook corrects permissions throughout keystone containers for all
log files.


remove-juno-log-rotate.yml
--------------------------

This playbook removes log rotation files that were created in the Juno
release. Log rotation processes in Kilo has been revised, and the Juno files
would conflict with the new processes.


mariadb-apt-cleanup.yml
-----------------------

In the Juno release, the apt sources for MariaDB used plaintext HTTP. This
playbook cleans up any lingering apt sources for MariaDB that use HTTP so that
the new HTTPS apt sources are used in Kilo.

nova-extra-migrations.yml
-------------------------

This playbook runs transitional extra migrations needed for nova. The playbook
will run a null instance uuid scan and the nova flavor migrations which will
clean up the database. Depending on the number of instances online this may
take some time. While the tasks within the playbook are optional, these steps
are recommended in order to future proofing the environment.


swift-ring-adjustments.yml
--------------------------

This playbook ensures that the Swift ring is located on the appropriate swift
nodes. This co-location of the swift ring ensures that the deployment host is
no longer a potential single point of failure for swift.


swift-repo-adjustments.yml
--------------------------

This playbook ensures that the Swift all swift nodes have access to the backports
repositories. This is required due to new dependencies on *liberasurecode*.


user-secrets-adjustments.yml
----------------------------

This playbook ensures that the user secrets file is updated based on the example
file in the main repository. This makes it possible to guarantee all secrets are
carried into the upgraded environment and appropriately generated.
