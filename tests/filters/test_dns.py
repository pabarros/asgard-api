# encoding: utf-8

import json
from unittest import TestCase, skip
from hollowman.filters.dns import DNSRequestFilter
from tests import RequestStub
import unittest
from hollowman.filters import Context
import mock

from marathon.models.app import MarathonApp


class DNSRequestFilterTest(TestCase):

    def setUp(self):
        self.ctx = Context(marathon_client=None, request=None)
        self.filter = DNSRequestFilter()

    def test_do_not_add_dns_entry_if_is_not_a_docker_app(self):
        """
         Only add if ['container']['docker'] exists
        """
        data_ = {
            "id": "/foo/bar",
            "cmd": "sleep 5000",
            "cpus": 1,
            "mem": 128,
            "disk": 0,
            "instances": 1,
            "container": {
                "volumes": [
                    {
                        "containerPath": "data",
                        "persistent": {
                            "size": 128
                        },
                        "mode": "RW"
                    }
                ],
                "type": "MESOS"
            }
        }
        request = RequestStub(path="/v2/apps/", data=data_)
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)
        self.assertFalse('docker' in modified_request.get_json()['container'])

    def test_add_dns_enty_when_app_has_no_docker_parameters(self):
        data_ = {
            "container": {
                "docker": {
                    "image": "alpine:3.4"
                }
            }
        }
        request = RequestStub(path="/v2/apps/", data=data_)
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)
        self.assertIsNotNone(modified_request)
        self.assertTrue('container' in modified_request.get_json())
        self.assertTrue('docker' in modified_request.get_json()['container'])
        self.assertTrue('parameters' in modified_request.get_json()[
                        'container']['docker'])

        docker_parameters = modified_request.get_json()['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))

        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

    def test_add_docker0_dns_entry_single_app(self):
        data_ = {
            "id": "/daltonmatos/sleep2",
            "cmd": "sleep 40000",
            "cpus": 1,
            "mem": 128,
            "disk": 0,
            "instances": 0,
            "container": {
                  "type": "DOCKER",
                  "docker": {
                      "image": "alpine:3.4",
                      "network": "BRIDGE",
                  },
            }
        }
        request = RequestStub(path="/v2/apps/", data=data_)
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)
        docker_parameters = modified_request.get_json()['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))

        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

    def test_add_docker0_dns_entry_when_updating_single_app(self):
        """
        Methos PUT: Matarhon-ui sends only the fileds that will be updated,
        Check if the `container` key is present on the body.
        """
        data_ = {
            "id": "/foo/bar",
            "env": {
                "PASSWD": "secre_"
            },
            "container": {
                "type": "DOCKER",
                "volumes": [],
                "docker": {
                    "image": "alpine:3.4",
                    "network": "BRIDGE",
                    "portMappings": [
                        {
                            "containerPort": 80,
                            "protocol": "tcp",
                            "name": "nginx"
                        }
                    ],
                }
            }
        }
        request = RequestStub(path="/v2/apps//foo/bar", data=data_)
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)

        docker_parameters = modified_request.get_json()['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

    def test_remove_any_unwanted_dns_entries_single_app(self):
        data_ = {
            "id": "/daltonmatos/sleep2",
            "cmd": "sleep 40000",
            "cpus": 1,
            "mem": 128,
            "instances": 0,
            "container": {
                "type": "DOCKER",
                "docker": {
                    "image": "alpine:3.4",
                    "parameters": [
                        {
                            "key": "dns",
                            "value": "8.8.8.8"
                        },
                        {
                            "key": "dns",
                            "value": "8.8.4.4"
                        }
                    ],
                }
            },
        }
        request = RequestStub(path="/v2/apps/", data=data_)
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)

        docker_parameters = modified_request.get_json()['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

    def test_remove_any_unwanted_dns_entry_multi_app(self):
        data_ = [
            {
                "id": "/s0",
                "cmd": "sleep 40000",
                "cpus": 1,
                "mem": 128,
                "instances": 0,
                "container": {
                    "type": "DOCKER",
                    "docker": {
                        "image": "alpine:3.4",
                        "parameters": [
                            {
                                "key": "dns",
                                "value": "8.8.8.8"
                            },
                        ],
                    }
                },
            },
            {
                "id": "/s1",
                "cmd": "sleep 40000",
                "cpus": 1,
                "mem": 128,
                "instances": 0,
                "container": {
                    "type": "DOCKER",
                    "docker": {
                        "image": "alpine:3.4",
                        "parameters": [
                            {
                                "key": "dns",
                                "value": "8.8.8.8"
                            },
                        ],
                    }
                },
            }
        ]
        request = RequestStub(path="/v2/apps/", data=data_)
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)

        docker_parameters = modified_request.get_json()[0]['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

        docker_parameters = modified_request.get_json()[1]['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

    def test_add_docker0_dns_entry_multi_appp(self):
        data_ = [
            {
                "id": "/sleep1",
                "cmd": "sleep 40000",
                "instances": 0,
                "container": {
                    "docker": {
                        "image": "alpine:3.4",
                    }
                },
            },
            {
                "id": "/sleep0",
                "cmd": "sleep 40000",
                "instances": 0,
                "container": {
                    "docker": {
                        "image": "alpine:3.4",
                    }
                },
            },
        ]
        request = RequestStub(path="/v2/apps/", data=data_)
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)

        docker_parameters = modified_request.get_json()[0]['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

        docker_parameters = modified_request.get_json()[1]['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

    @unittest.skip("Ainda nao implementado")
    def test_add_consul_instances_dns_entry_single_app(self):
        self.fail()

    @unittest.skip("Ainda nao implementado")
    def test_add_consul_instances_dns_when_updating_single_app(self):
        self.fail()

    @unittest.skip("Ainda nao implementado")
    def test_add_consul_instances_dns_entry_multi_app(self):
        self.fail()

    @unittest.skip("Ainda nao implementado")
    def test_add_consul_instances_dns_when_updating_multi_app(self):
        self.fail()

    def test_add_dns_entry_when_creating_1_depth_apps_via_groups_endpoint(self):
        data_ = {
            "id": "/",
            "apps": [
                {
                    "id": "/appfoo",
                  "instances": 2,
                  "cpus": 1,
                  "mem": 1024,
                  "disk": 0,
                  "container": {
                      "type": "DOCKER",
                    "docker": {
                        "image": "alpine:3.4",
                      "network": "BRIDGE",
                    }
                  }
                },
                {
                    "id": "/appbar",
                    "instances": 2,
                    "cpus": 1,
                    "mem": 1024,
                    "disk": 0,
                    "container": {
                        "type": "DOCKER",
                        "docker": {
                            "image": "alpine:3.4",
                            "network": "BRIDGE",
                        }
                    }
                },


            ],
        }
        request = RequestStub(path="/v2/groups/", data=data_)
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)

        docker_parameters = modified_request.get_json()['apps'][0]['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

        docker_parameters = modified_request.get_json()['apps'][1]['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

    def test_add_dns_entry_on_creating_2_depth_groups_with_apps_via_groups_endpoint(self):
        """
         Podemos criar apps ao mesmo tempo que criamos groups. Esse teste verifica o seguinte:
         Group.
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
        # This crates: /group/tools/appone, /group/tools/bla/apptwo
        data_ = {
            "id": "/group/",
            "apps": [],
            "groups": [
                {
                  "id": "/group/tools",
                  "apps": [
                      {
                          "id": "/group/tools/appone",
                          "container": {
                              "docker": {
                                  "image": "alpine:3.4",
                                  "network": "BRIDGE"
                              }
                          }
                      }
                  ],
                    "groups": [
                      {
                          "id": "/group/tools/bla",
                          "apps": [
                              {
                                  "id": "/group/tools/bla/apptwo",
                                  "container": {
                                      "docker": {
                                          "image": "alpine:3.4",
                                          "network": "BRIDGE"
                                      }
                                  }
                              }
                          ]

                      }
                  ]
                }
            ]
        }

        request = RequestStub(path="/v2/groups/", data=data_)
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)

        docker_parameters = modified_request.get_json()['groups'][0]['apps'][0][
            'container']['docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

        docker_parameters = modified_request.get_json()['groups'][0]['groups'][0][
            'apps'][0]['container']['docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

    def test_allow_other_parameters_among_with_dns(self):
        data = [
            {
                "id": "/sleep1",
                "cmd": "sleep 40000",
                "instances": 0,
                "container": {
                    "docker": {
                        "image": "alpine:3.4",
                        "parameters" : [
                            {
                                "key": "entrypoint",
                                "value": "/my_custom_entrypoint.sh"
                            }
                        ]
                    }
                }
            }
        ]
        request = RequestStub(path="/v2/apps/", data=data)
        self.ctx.request = request

        json_filtered_request = self.filter.run(self.ctx).get_json()
        params_dict = dict((param['key'], param) for param in json_filtered_request[0]['container']['docker']['parameters'])
        self.assertEqual(len(json_filtered_request[0]['container']['docker']['parameters']), 2)
        self.assertDictEqual(params_dict['dns'], {"key": "dns", "value": "172.17.0.1"})

    def test_add_dns_when_patching_only_envvars_app_without_envs(self):
        """
        Temos que pegar PUT em /v2/apps/<app-name> contendo apenas a modificação das envs.
        """
        original_app = {
                u"id": u"/app/foo",
                u"cmd": u"sleep 40000",
                u"instances": 0,
                u"container": {
                    u"docker": {
                        u"image": u"alpine:3.4",
                        u"forcePullImage": False,
                        u"network": u"BRIDGE",
                        u"privileged": False,
                    },
                    u"type": u"DOCKER",
                },
        }
        data_ = {
            u"env": {
                u"MY_ENV": u"abc",
                u"OTHER_ENV": u"123",
            }
        }

        modified_app = original_app.copy()
        modified_app[u'container'][u'docker'][u'parameters'] = [
                    {
                        u"key": u"dns",
                        u"value": u"172.17.0.1"
                    }
        ]
        modified_app.update(data_)

        with mock.patch.object(self, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps//app/foo", data=data_, method="PUT")
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**original_app)
            ctx_mock.request = request

            filtered_request = self.filter.run(ctx_mock)
            ctx_mock.marathon_client.get_app.assert_called_with("/app/foo")
            self.assertDictEqual(modified_app, filtered_request.get_json())

    def test_add_dns_when_patching_only_envvars_app_with_envs(self):
        self.maxDiff = None

        """
        Temos que pegar PUT em /v2/apps/<app-name> contendo apenas a modificação das envs.
        """
        original_app = {
                u"id": u"/app/foo",
                u"cmd": u"sleep 40000",
                u"instances": 0,
                u"container": {
                    u"docker": {
                        u"image": u"alpine:3.4",
                        u"forcePullImage": False,
                        u"network": u"BRIDGE",
                        u"privileged": False,
                    },
                    u"type": u"DOCKER",
                },
                u"env": {
                    "HAS_ENV": "abc",
                    "MY_ENV": "other-value",
                }
        }
        data_ = {
            u"env": {
                u"MY_ENV": u"abc",
                u"OTHER_ENV": u"123",
            }
        }

        modified_app = original_app.copy()
        modified_app[u'container'][u'docker'][u'parameters'] = [
                    {
                        u"key": u"dns",
                        u"value": u"172.17.0.1"
                    }
        ]
        modified_app['env'].update(data_['env'])

        with mock.patch.object(self, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps//app/foo", data=data_, method="PUT")

            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**original_app)
            ctx_mock.request = request
            filtered_request = self.filter.run(ctx_mock)
            ctx_mock.marathon_client.get_app.assert_called_with("/app/foo")
            self.assertDictEqual(modified_app, filtered_request.get_json())

    def test_do_not_add_dns_entries_if_disablelabel_present_no_parameters(self):
        """
        Se a label hollowman.filter.dns.disable estiver presente, nenhum dns server será
        adicionado para essa app
        """
        data_ = {
            "id": "/app/foo",
            "labels": {
                "hollowman.filter.dns.disable": "true"
            },
            u"container": {
                u"docker": {
                    u"image": u"alpine:3.4",
                    u"forcePullImage": False,
                    u"network": u"BRIDGE",
                    u"privileged": False,
                },
                u"type": u"DOCKER",
            },

        }

        with mock.patch.object(self, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps//app/foo", data=data_, method="PUT")

            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data_)
            ctx_mock.request = request
            filtered_request = self.filter.run(ctx_mock)
            self.assertTrue('parameters' not in filtered_request.get_json()['container']['docker'])

    def test_do_not_add_dns_entries_if_disablelabel_present_app_with_parameters(self):
        """
        Se a label hollowman.filter.dns.disable estiver presente, nenhum dns server será
        adicionado para essa app
        """
        parameters_ = [
            {u"key": u"param", u"value": u"42"}
        ]
        data_ = {
            "id": "/app/foo",
            "labels": {
                "hollowman.filter.dns.disable": "true"
            },
            u"container": {
                u"docker": {
                    u"image": u"alpine:3.4",
                    u"forcePullImage": False,
                    u"network": u"BRIDGE",
                    u"privileged": False,
                    u"parameters": parameters_,
                },
                u"type": u"DOCKER",
            },

        }

        with mock.patch.object(self, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps//app/foo", data=data_, method="PUT")

            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data_)
            ctx_mock.request = request
            filtered_request = self.filter.run(ctx_mock)
            self.assertEqual(parameters_, filtered_request.get_json()['container']['docker']['parameters'])

    def test_network_host_app_left_intact(self):
        """
        When the app is on network=HOST mode we shouldn't mess with it.
        """
        data_ = {
            "id": "/foo/sleep2",
            "cmd": "sleep 40000",
            "cpus": 1,
            "mem": 128,
            "disk": 0,
            "instances": 0,
            "container": {
                  "type": "DOCKER",
                  "docker": {
                      "image": "alpine:3.4",
                      "network": "HOST",
                  },
            }
        }

        with mock.patch.object(self, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps//foo/sleep2", data=data_)

            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data_)
            ctx_mock.request = request
            modified_request = self.filter.run(ctx_mock)
            self.assertFalse("parameters" in modified_request.get_json()['container']['docker'])
