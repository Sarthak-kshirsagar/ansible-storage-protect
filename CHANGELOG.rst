============================================
ibm.storage_protect Release Notes
============================================

.. contents:: Topics


v1.0.0
======

Major Changes
-------------

- Added dsm_sysfile module to allow creation of dsm.sys file
- Added node module to create node
- Added nodes role to wrap around node module
- Added schedule module to create schedules
- Added schedules role to wrap around schedule module

Minor Changes
-------------

- Add ability to associate a schedule to a node in node module
- Add global_vars role as a 'meta dependency' role for including vars to the other roles.

Bugfixes
--------

