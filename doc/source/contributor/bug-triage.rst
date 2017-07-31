============================
OpenStack-Ansible Bug Triage
============================

What is a bug triage
~~~~~~~~~~~~~~~~~~~~

"Bug triage is a process where tracker issues are screened and
prioritised. Triage should help ensure we appropriately manage all
reported issues - bugs as well as improvements and feature requests."
(Source: `Moodle bug triage`_)

.. _Moodle bug triage: https://docs.moodle.org/dev/Bug_triage

Reported bugs need confirmation, prioritization, and ensure they do not
go stale. If you care about OpenStack stability but are not wanting to
actively develop the roles and playbooks used within the OpenStack-Ansible
project, consider contributing in the area of bug triage.

The bug triage practices in OpenStack-Ansible are based on the
`OpenStack Bug Triage Documentation`_ and on the `Nova Bug triage page`_.

.. _Nova Bug triage page: https://wiki.openstack.org/wiki/Nova/BugTriage
.. _OpenStack Bug Triage Documentation: https://docs.openstack.org/infra/manual/developers.html#working-on-bugs

Bug classification
~~~~~~~~~~~~~~~~~~

The **Status** of a bug is one of the following:

* *New* - The bug was just created.
* *Incomplete* - The bug is waiting on input from the reporter.
* *Confirmed* - The bug was reproduced or confirmed as a genuine bug.
* *Triaged* - The bug comments contain a full analysis on how to
  properly fix the issue.
* *In Progress* - Work on the fix is in progress and the bug has an assignee.
* *Fix Committed* - The branch containing the fix was merged into
  the master branch.
* *Fix Released* - The fix is included in the proposed branch, a past
  milestone or a past release.
* *Invalid* - This is not a bug.
* *Opinion* - This is a valid issue, but it is an opinion of the reporter.
* *Won't Fix* - This is a valid issue, but we do not intend to fix that.

The **Importance** of a bug is one of the following:

* *Critical* - The bug can take down infrastructures, or gates are
  blocked. Handle as soon as possible.
* *High* - Schedule to be fixed soon.
* *Medium* - Fix when convenient, or schedule to fix later.
* *Low* - Fix when convenient.
* *Wishlist* - Not a bug. It is an enhancement or a new feature.
* *Undecided* - Not decided yet. It might need more discussion.

Bug triage meeting duties
~~~~~~~~~~~~~~~~~~~~~~~~~

If the bug description is incomplete, or the report is lacking the
information necessary to reproduce the issue, ask the reporter to
provide missing information, and set the bug status to
*Incomplete*

If the bug report contains enough information and you can reproduce it (or
it looks valid), then you should set its status to *Confirmed*.

If the bug has security implications, set the security flag
(under "This report is public" on the top right)

If the bug affects a specific area covered by an official tag, you should
set the tag. For example, if the bug is likely to be quite easy to solve,
add the `low-hanging-fruit` tag.

The bug triage meeting is probably a good time for people with bug
supervisors rights to also prioritize bugs per importance (on top of
classifying them on status).

Bug skimming duty
~~~~~~~~~~~~~~~~~

To help triaging bugs, one person of the bug team can be on "bug
skimming duty".

:Q: What is the goal of the bug skimming duty?
:A: Bug skimming duty reduces the amount of work other developers have to
    spend to do a proper root cause analysis (and later fix) of bug reports.
    For this, close the obviously invalid bug reports, confirm the
    obviously valid bug reports, ask questions if things are unclear.

:Q: Do I need to prove that a bug report is valid/invalid before I can
    set it to *Confirmed*/*Invalid* ?
:A: No. Sometimes it is not even possible because you do not have the
    resources. Looking at the code and tests often enables you to make
    an educated guess. Citing your sources in a comment helps the
    discussion.

:Q: What is the best status to close a bug report if its issue cannot be
    reproduced?
:A: Definitively *Invalid*. The status *Incomplete* is an open state
    and means that more information is necessary.

:Q: How do I handle open bug reports which are Incomplete for too long?
:A: If it is in this state for more than 30 days and no answers to the
    open questions are given, close it with Won't Fix.

:Q: How do I handle dependencies to other bugs or TBD features in other
    projects? For example, I can fix a bug in OpenStack-Ansible but I
    need that a feature in Compute (nova) gets implemented before.
:A: Leave a comment in the OpenStack-Ansible bug report which explains
    this dependency and leave a link to the blueprint or bug report of
    the other project you depend on.

:Q: Do I have to double-check bug reports which are New and have an
    assignee?
:A: Usually not. This bug report has an inconsistent state though.
    If a bug report has an assignee, it should be In Progress and have
    an importance set.

Bug skimming duty weekly checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Prioritize or reprioritize OpenStack-Ansible `confirmed bugs`_.

- Move year old `wishlist bugs`_ to Opinion/Wishlist to remove clutter.
  You can use the following message:

    This wishlist bug has been open a year without any activity. I am
    moving this to "Opinion / Wishlist". This is an easily-obtainable
    queue of older requests. This bug can be reopened
    (set back to "New") if someone decides to work on this.

- Move bugs that can not be reproduced to an invalid state if they are
  unmodified for more than a month.

- Send an email to the openstack-dev list with the `list of bugs to
  triage`_ during the week. A new bug marked as *Critical* or *High* must
  be treated in priority.

.. _confirmed bugs: https://bugs.launchpad.net/openstack-ansible/+bugs?field.searchtext=&orderby=-importance&field.status%3Alist=CONFIRMED&field.status%3Alist=TRIAGED&field.status%3Alist=INPROGRESS&assignee_option=any&field.assignee=&field.bug_reporter=&field.bug_commenter=&field.subscriber=&field.structural_subscriber=&field.tag=&field.tags_combinator=ANY&field.has_cve.used=&field.omit_dupes.used=&field.omit_dupes=on&field.affects_me.used=&field.has_patch.used=&field.has_branches.used=&field.has_branches=on&field.has_no_branches.used=&field.has_no_branches=on&field.has_blueprints.used=&field.has_blueprints=on&field.has_no_blueprints.used=&field.has_no_blueprints=on&search=Search

.. _wishlist bugs: https://bugs.launchpad.net/openstack-ansible/+bugs?field.searchtext=&orderby=datecreated&search=Search&field.importance%3Alist=WISHLIST&assignee_option=any&field.assignee=&field.bug_reporter=&field.bug_commenter=&field.subscriber=&field.structural_subscriber=&field.tag=&field.tags_combinator=ANY&field.has_cve.used=&field.omit_dupes.used=&field.omit_dupes=on&field.affects_me.used=&field.has_patch.used=&field.has_branches.used=&field.has_branches=on&field.has_no_branches.used=&field.has_no_branches=on&field.has_blueprints.used=&field.has_blueprints=on&field.has_no_blueprints.used=&field.has_no_blueprints=on

.. _list of bugs to triage: https://bugs.launchpad.net/openstack-ansible/+bugs?search=Search&field.status=New
