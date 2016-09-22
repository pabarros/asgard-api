from unittest import TestCase


class ForceDNSTest(TestCase):

  def test_add_docker0_dns_entry_single_app(self):
    self.fail()

  def test_add_docker0_dns_entry_when_updating_single_app(self):
    self.fail()

  def test_remove_any_unwanted_dns_entries_single_app(self):
    self.fail()

  def test_remove_any_unwanted_dns_entry_multi_app(self):
    self.fail()

  def test_add_docker0_dns_entry_multi_appp(self):
    self.fail()

  def test_add_docker0_dns_entry_when_updating_multi_app(self):
    self.fail()

  def test_add_consul_instances_dns_entry_single_app(self):
    self.fail()

  def test_add_consul_instances_dns_when_updating_single_app(self):
    self.fail()

  def test_add_consul_instances_dns_entry_multi_app(self):
    self.fail()

  def test_add_consul_instances_dns_when_updating_multi_app(self):
    self.fail()

  def test_add_dns_entry_when_creating_app_via_groups_endpoint(self):
    self.fail()

  def test_add_dns_entry_on_creating_2_depth_groups_with_apps_via_groups_endpoint(self):
    """
     Podemos criar apps ao mesmo tempo que criamos groups. Esse teste verifica o seguinte:
     Group.json
      {
        "id": "/"
        "groups": {
            "id": "/my",
            "apps": [
                /* Apps definition */
            ],
            "groups": {
                "id": "/other",
                "apps": {
                    /* Apps definition */
                }
            }
        }

      }
    """
    self.fail()

  def test_add_dns_entry_via_groups_id_endpoint(self):
    """
    O mesmo que pdoemos fazer via /v2/groups, podemos fazer /v2/group/<group_id>
    HTTP POST
    """
    self.fail()

  def test_add_dns_entry_via_groups_is_endpoint_multi_depth(self):
    self.fail()
