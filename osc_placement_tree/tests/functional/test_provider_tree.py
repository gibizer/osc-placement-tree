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
import os
import subprocess

from osc_placement_tree.tests.functional import base
from osc_placement_tree.tests import uuids


class TestProviderTree(base.TestBase):
    @classmethod
    def setUpClass(cls):
        super(TestProviderTree, cls).setUpClass()
        try:
            cls._create_test_data()
        except Exception:
            cls.doClassCleanup()
            raise

    @classmethod
    def _create_test_data(cls):
        cls.create_rp("compute0_with_disk")
        cls.set_traits(
            "compute0_with_disk",
            ["HW_CPU_X86_SSE2", "HW_CPU_X86_SSE", "HW_CPU_X86_MMX"],
        )
        cls.create_rp(
            "compute0_with_disk_NUMA0", parent_rp_name="compute0_with_disk"
        )
        cls.create_rp(
            "compute0_with_disk_NUMA1", parent_rp_name="compute0_with_disk"
        )

        cls.update_inventory(
            "compute0_with_disk", "DISK_GB=256", "DISK_GB:reserved=16"
        )

        cls.update_inventory(
            "compute0_with_disk_NUMA0",
            "VCPU=4",
            "VCPU:allocation_ratio=16.0",
            "VCPU:reserved=1",
            "MEMORY_MB=16384",
            "MEMORY_MB:reserved=1024",
        )

        cls.update_inventory(
            "compute0_with_disk_NUMA1",
            "VCPU=4",
            "VCPU:allocation_ratio=16.0",
            "MEMORY_MB=16384",
        )

        cls.create_rp("compute1_with_disk")
        cls.set_traits("compute1_with_disk", ["HW_CPU_X86_MMX"])
        cls.create_rp(
            "compute1_with_disk_NUMA0", parent_rp_name="compute1_with_disk"
        )
        cls.create_rp(
            "compute1_with_disk_NUMA1", parent_rp_name="compute1_with_disk"
        )

        cls.update_inventory(
            "compute1_with_disk", "DISK_GB=128", "DISK_GB:reserved=16"
        )

        cls.update_inventory(
            "compute1_with_disk_NUMA0",
            "VCPU=8",
            "VCPU:allocation_ratio=16.0",
            "VCPU:reserved=1",
            "MEMORY_MB=16384",
            "MEMORY_MB:reserved=1024",
        )

        cls.update_inventory(
            "compute1_with_disk_NUMA1",
            "VCPU=8",
            "VCPU:allocation_ratio=16.0",
            "MEMORY_MB=16384",
        )

        cls.set_aggregate(
            "compute0_with_disk", [uuids.host_aggregate1, uuids.agg2]
        )
        cls.set_aggregate(
            "compute1_with_disk", [uuids.host_aggregate1, uuids.agg2]
        )

        cls.set_aggregate("compute0_with_disk_NUMA0", [uuids.agg2])
        cls.set_aggregate("compute0_with_disk_NUMA1", [uuids.agg2])
        cls.set_aggregate("compute1_with_disk_NUMA0", [uuids.agg2])
        cls.set_aggregate("compute1_with_disk_NUMA1", [uuids.agg2])

        project_id = cls.get_project_id(os.environ["OS_PROJECT_NAME"])
        user_id = cls.get_user_id(os.environ["OS_USERNAME"])

        cls.create_allocation(
            uuids.consumer1,
            allocations={
                "compute0_with_disk": {"DISK_GB": 10},
                "compute0_with_disk_NUMA0": {"VCPU": 1},
                "compute0_with_disk_NUMA1": {"MEMORY_MB": 1024},
            },
            project_id=project_id,
            user_id=user_id,
        )
        cls.create_allocation(
            uuids.consumer2,
            allocations={
                "compute1_with_disk": {"DISK_GB": 40},
                "compute1_with_disk_NUMA1": {"VCPU": 4, "MEMORY_MB": 8192},
            },
            project_id=project_id,
            user_id=user_id,
        )
        cls.create_allocation(
            uuids.consumer3,
            allocations={
                "compute1_with_disk": {"DISK_GB": 20},
                "compute1_with_disk_NUMA0": {"VCPU": 2, "MEMORY_MB": 4096},
            },
            project_id=project_id,
            user_id=user_id,
        )

    def test_provider_tree_show(self):
        dot_src = self.openstack(
            "resource provider tree show %s" % uuids.compute0_with_disk
        )
        self.assertDot(dot_src)

    def test_provider_tree_show_with_fields(self):
        dot_src = self.openstack(
            "resource provider tree show %s "
            "--fields uuid,name,generation" % uuids.compute0_with_disk
        )
        self.assertDot(dot_src)

    def test_provider_tree_show_not_existing_uuid(self):
        ex = self.assertRaises(
            subprocess.CalledProcessError,
            self.openstack,
            "resource provider tree show %s" % uuids.not_existing_rp,
        )
        self.assertIn("does not exists", ex.output)

    def test_provider_tree_show_with_consumers(self):
        dot_src = self.openstack(
            "resource provider tree show %s "
            "--show_consumers" % uuids.compute0_with_disk
        )
        self.assertDot(dot_src)

    def test_provider_tree_list(self):
        dot_src = self.openstack("resource provider tree list")
        self.assertDot(dot_src)

    def test_provider_tree_list_with_fields(self):
        dot_src = self.openstack(
            "resource provider tree list " "--fields uuid,name,generation"
        )
        self.assertDot(dot_src)

    def test_provider_tree_list_with_consumers(self):
        dot_src = self.openstack(
            "resource provider tree list " "--show_consumers"
        )
        self.assertDot(dot_src)
