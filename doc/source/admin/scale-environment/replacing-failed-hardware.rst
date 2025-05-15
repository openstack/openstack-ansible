Replacing failed hardware
~~~~~~~~~~~~~~~~~~~~~~~~~

It is essential to plan and know how to replace failed hardware in your cluster
without compromising your cloud environment.

Consider the following to help establish a hardware replacement plan:

- What type of node am I replacing hardware on?
- Can the hardware replacement be done without the host going down? For
  example, a single disk in a RAID-10.
- If the host DOES have to be brought down for the hardware replacement, how
  should the resources on that host be handled?

If you have a Compute (nova) host that has a disk failure on a
RAID-10, you can swap the failed disk without powering the host down. On the
other hand, if the RAM has failed, you would have to power the host down.
Having a plan in place for how you will manage these types of events is a vital
part of maintaining your OpenStack environment.

For a Compute host, shut down the instance on the host before
it goes down. For a Block Storage (cinder) host using non-redundant storage,
shut down any instances with volumes attached that require that mount point.
Unmount the drive within your operating system and re-mount the drive once the
Block Storage host is back online.
