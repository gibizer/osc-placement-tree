.. image:: https://travis-ci.org/gibizer/osc-placement-tree.svg?branch=master
    :target: https://travis-ci.org/gibizer/osc-placement-tree

==================
osc-placement-tree
==================

OpenStackClient plugin for advanced operations for the Placement service

This is an OpenStackClient plugin, that provides extra CLI commands for the
Placement service to visualize what is stored in placement.

* Free software: Apache license


Examples
--------
Use it from the ``openstack`` CLI:

.. code:: bash

  $ openstack resource provider tree list | dot -Tsvg

.. image:: doc/example.svg


Use it in placement functional test environment:

.. code:: python

    from osc_placement_tree import utils as placement_visual
    from placement import direct

    with direct.PlacementDirect(
            self.conf_fixture.conf, latest_microversion=True) as client:
        placement_visual.dump_placement_db_to_dot(
            placement_visual.PlacementDirectAsClientWrapper(client),
            '/tmp/dump.dot')


Use it in nova functional test environment:

.. code:: python

    from osc_placement_tree import utils as placement_visual

    placement_visual.dump_placement_db_to_dot(
        placement_visual.PlacementFixtureAsClientWrapper(
            self.placement_api),
        '/tmp/dump.dot')

