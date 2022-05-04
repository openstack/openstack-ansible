Compatibility Matrix
--------------------

All of the OpenStack-Ansible releases are compatible with specific sets of
operating systems and their versions. Operating Systems have their own
lifecycles, however we may drop their support before end of their EOL because
of various reasons:

 * OpenStack requires a higher version of a library (ie. libvirt)
 * Python version
 * specific dependencies
 * etc.

However, we do try to provide ``upgrade`` releases where we support both new
and old Operating System versions, providing deployers the ability to
properly upgrade their deployments to the new Operating System release.

In CI we test upgrades from N to N+1 releases and only for source deployments.

Below you will find the support matrix of Operating Systems for
OpenStack-Ansible releases.

Operating systems with experimental support are marked with ``E`` in the table.

.. raw:: html
    :file: os-compatibility-matrix.html
