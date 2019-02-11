from asynctest import TestCase


from asgard.backends.mesos import MesosTask


class MesosTaskTest(TestCase):
    async def test_transform_mesos_task_name_to_asgard_task_name(self):
        original_task_name = (
            "infra_scoutapp_mesos-master.a34109d3-2b99-11e9-a3c9-d2a7ebde729b"
        )
        self.assertEqual(
            "scoutapp_mesos-master.a34109d3-2b99-11e9-a3c9-d2a7ebde729b",
            MesosTask._transform_to_asgard_task_name(original_task_name),
        )
