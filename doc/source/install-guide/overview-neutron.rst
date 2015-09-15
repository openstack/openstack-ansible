`Home <index.html>`_ OpenStack-Ansible Installation Guide

OpenStack Networking
--------------------

OpenStack Networking (neutron) is configured to use a DHCP agent, L3
Agent and Linux Bridge agent within a networking agents container.
`Figure 2.5, "Networking agents
containers" <overview-neutron.html#fig_overview_neutron-agents>`_
shows the interaction of these agents, network components, and
connection to a physical network.

 

**Figure 2.5. Networking agents containers**

.. image:: figures/networking-neutronagents.png

The Compute service uses the KVM hypervisor. `Figure 2.6, "Compute
hosts" <overview-neutron.html#fig_overview_neutron-compute>`_ shows
the interaction of instances, Linux Bridge agent, network components,
and connection to a physical network.

 

**Figure 2.6. Compute hosts**

.. image:: figures/networking-compute.png

--------------

.. include:: navigation.txt
