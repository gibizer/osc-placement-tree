# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from osc_placement_tree.tests.functional import base
from osc_placement_tree.tests import uuids


class TestProviderTree(base.TestBase):

    def setUp(self):
        super(TestProviderTree, self).setUp()

        self.create_rp(uuids.compute0_with_disk)
        self.create_rp(uuids.compute0_with_disk_NUMA0,
                       parent_rp_uuid=uuids.compute0_with_disk)
        self.create_rp(uuids.compute0_with_disk_NUMA1,
                       parent_rp_uuid=uuids.compute0_with_disk)

        self.update_inventory(uuids.compute0_with_disk,
                              'DISK_GB=256',
                              'DISK_GB:reserved=16')

        self.update_inventory(uuids.compute0_with_disk_NUMA0,
                              'VCPU=4',
                              'VCPU:allocation_ratio=16.0',
                              'VCPU:reserved=1',
                              'MEMORY_MB=16384',
                              'MEMORY_MB:reserved=1024')

        self.update_inventory(uuids.compute0_with_disk_NUMA1,
                              'VCPU=4',
                              'VCPU:allocation_ratio=16.0',
                              'MEMORY_MB=16384')

        self.create_rp(uuids.compute1_with_disk)
        self.create_rp(uuids.compute1_with_disk_NUMA0,
                       parent_rp_uuid=uuids.compute1_with_disk)
        self.create_rp(uuids.compute1_with_disk_NUMA1,
                       parent_rp_uuid=uuids.compute1_with_disk)

        self.update_inventory(uuids.compute1_with_disk,
                              'DISK_GB=128',
                              'DISK_GB:reserved=16')

        self.update_inventory(uuids.compute1_with_disk_NUMA0,
                              'VCPU=8',
                              'VCPU:allocation_ratio=16.0',
                              'VCPU:reserved=1',
                              'MEMORY_MB=16384',
                              'MEMORY_MB:reserved=1024')

        self.update_inventory(uuids.compute1_with_disk_NUMA1,
                              'VCPU=8',
                              'VCPU:allocation_ratio=16.0',
                              'MEMORY_MB=16384')

    def test_provider_tree_show(self):
        dot_src = self.openstack('resource provider tree show %s' %
                                 uuids.compute0_with_disk)
        self.assertDot(dot_src)

    def test_provider_tree_list(self):
        dot_src = self.openstack('resource provider tree list')
        self.assertDot(dot_src)
