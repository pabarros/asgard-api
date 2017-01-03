# encoding: utf-8

import json
from unittest import TestCase
from hollowman.filters.dns import DNSRequestFilter


class RequestStub(object):

    def __init__(self, data=None, headers=None, is_json=True):
        self.data = json.dumps(data)
        self.headers = headers
        self.is_json = is_json

    def get_json(self):
        return json.loads(self.data)


class DNSRequestFilterTest(TestCase):

    def setUp(self):
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
        request = RequestStub(data=data_)
        modiified_request = self.filter.run(request)
        self.assertFalse('docker' in modiified_request.get_json()['container'])

    def test_add_dns_enty_when_app_has_no_docker_parameters(self):
        data_ = {
            "container": {
                "docker": {
                    "image": "alpine:3.4"
                }
            }
        }
        request = RequestStub(data=data_)
        dnsFilter = DNSRequestFilter()
        modiified_request = dnsFilter.run(request)
        self.assertIsNotNone(modiified_request)
        self.assertTrue('container' in modiified_request.get_json())
        self.assertTrue('docker' in modiified_request.get_json()['container'])
        self.assertTrue('parameters' in modiified_request.get_json()[
                        'container']['docker'])

        docker_parameters = modiified_request.get_json()['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))

        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

    def test_is_group(self):
        data_ = {
            "id": "/",
            "groups": [
                {
                  "id": "/bla"
                },
                {
                    "id": "/foo"
                }
            ]
        }
        self.assertTrue(self.filter.is_group(data_))
        data_ = {
            "id": "/abc",
            "container": {
                "docker": {
                }
            }
        }
        self.assertFalse(self.filter.is_group(data_))

    def test_get_apps_from_groups(self):
        data_ = {"id": "/"}
        self.assertEqual([], self.filter.get_apps_from_group(data_))

        data_ = {
            "id": "/",
            "apps": [
                {},
                {},
                {},
            ]
        }
        self.assertEqual([{}, {}, {}], self.filter.get_apps_from_group(data_))

    def test_is_docker_app(self):
        data_ = {
            "id": "/",
            "apps": [],
            "groups": []
        }
        self.assertFalse(self.filter.is_docker_app(data_))
        data_ = {
            "id": "/foo",
            "container": {
                "docker": {
                    "image": "alpine:3.4"
                }
            }
        }
        self.assertTrue(self.filter.is_docker_app(data_))

    def test_is_single_app(self):
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
        self.assertTrue(self.filter.is_single_app(data_))
        data_ = {"id": "/foo", "apps": {}}
        self.assertFalse(self.filter.is_single_app(data_))
        data_ = {"id": "/foo", "groups": {}}
        self.assertFalse(self.filter.is_single_app(data_))

        data_ = [
            {"id": "/foo"},
            {"id": "/bar"}
        ]
        self.assertFalse(self.filter.is_single_app(data_))

    def test_is_multi_app(self):
        data_ = [
            {"id": "/foo"},
            {"id": "/bar"}
        ]
        self.assertTrue(self.filter.is_multi_app(data_))

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
        request = RequestStub(data=data_)
        modiified_request = self.filter.run(request)
        docker_parameters = modiified_request.get_json()['container'][
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
        request = RequestStub(data=data_)
        modiified_request = self.filter.run(request)

        docker_parameters = modiified_request.get_json()['container'][
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
        request = RequestStub(data=data_)
        modiified_request = self.filter.run(request)

        docker_parameters = modiified_request.get_json()['container'][
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
        request = RequestStub(data=data_)
        modiified_request = self.filter.run(request)

        docker_parameters = modiified_request.get_json()[0]['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

        docker_parameters = modiified_request.get_json()[1]['container'][
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
        request = RequestStub(data=data_)
        modiified_request = self.filter.run(request)

        docker_parameters = modiified_request.get_json()[0]['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

        docker_parameters = modiified_request.get_json()[1]['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

    def test_add_consul_instances_dns_entry_single_app(self):
        self.fail()

    def test_add_consul_instances_dns_when_updating_single_app(self):
        self.fail()

    def test_add_consul_instances_dns_entry_multi_app(self):
        self.fail()

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
                      "network": "HOST",
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
                            "network": "HOST",
                        }
                    }
                },


            ],
        }
        request = RequestStub(data=data_)
        modiified_request = self.filter.run(request)

        docker_parameters = modiified_request.get_json()['apps'][0]['container'][
            'docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

        docker_parameters = modiified_request.get_json()['apps'][1]['container'][
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
                                  "network": "HOST"
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
                                          "network": "HOST"
                                      }
                                  }
                              }
                          ]

                      }
                  ]
                }
            ]
        }

        request = RequestStub(data=data_)
        modiified_request = self.filter.run(request)

        docker_parameters = modiified_request.get_json()['groups'][0]['apps'][0][
            'container']['docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])

        docker_parameters = modiified_request.get_json()['groups'][0]['groups'][0][
            'apps'][0]['container']['docker']['parameters']
        self.assertEqual(1, len(docker_parameters))
        self.assertEqual("dns", docker_parameters[0]['key'])
        self.assertEqual("172.17.0.1", docker_parameters[0]['value'])
