
import unittest
from marathon.models.group import MarathonGroup

from hollowman.marathon.group import AsgardAppGroup

class GroupWrapperTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_eq(self):
        root_a = AsgardAppGroup.from_json({"id": "/"})
        root_b = AsgardAppGroup.from_json({"id": "/"})
        self.assertEqual(root_a, root_b)

    def test_from_json(self):
        data = {
            "id": "/",
            "apps": [],
            "groups": [],
        }
        group = AsgardAppGroup.from_json(data)
        self.assertEqual("/", group.id)

    def test_iterate_empty_group(self):
        group = AsgardAppGroup()
        apps = list(group.iterate_apps())
        self.assertEqual(0, len(apps))

    def test_iterate_sub_groups_one_level(self):
        data = {
            "id": "/",
            "groups": [
                {"id": "/foo", "apps": []},
                {"id": "/bla", "apps": []},
            ],
            "apps": []
        }
        group = AsgardAppGroup(MarathonGroup.from_json(data))
        self.assertEqual(group.id, "/")
        all_group_ids = ["/", "/foo", "/bla"]
        self.assertEqual(all_group_ids, [g.id for g in group.iterate_groups()])

    def test_iterate_sub_groups_two_levels(self):
        """
        Grupos:
            + /
              + /foo
                + /bla
        """
        data = {
            "id": "/",
            "groups": [
                {
                    "id": "/foo",
                    "apps": [],
                    "groups": [
                        {
                            "id": "/foo/bar",
                            "apps": []
                        },
                    ]
                },
            ],
            "apps": []
        }
        group = AsgardAppGroup(MarathonGroup.from_json(data))
        self.assertEqual(group.id, "/")
        expected_all_group_ids = ["/", "/foo", "/foo/bar"]
        returned_groups = list(group.iterate_groups())
        self.assertEqual(expected_all_group_ids, [g.id for g in returned_groups])

    def test_iterate_sub_groups_three_levels(self):
        """
        Grupos:
            + /
              + /foo
                + /bla
                  + /baz
        """
        data = {
            "id": "/",
            "groups": [
                {
                    "id": "/foo",
                    "apps": [],
                    "groups": [
                        {
                            "id": "/foo/bar",
                            "apps": [],
                            "groups": [{"id": "/foo/bar/baz"}]
                        },
                    ]
                },
            ],
            "apps": []
        }

        group = AsgardAppGroup(MarathonGroup.from_json(data))
        self.assertEqual(group.id, "/")
        expected_all_group_ids = ["/", "/foo", "/foo/bar", "/foo/bar/baz"]
        returned_groups = list(group.iterate_groups())
        self.assertEqual(expected_all_group_ids, [g.id for g in returned_groups])

    def test_iterate_subgroups_three_levels_with_siblings(self):
        """
        Grupos:
            + /
              + /foo
                + /bar
                  + /foo/bar/baz
              + /foo2
        """
        data = {
            "id": "/",
            "groups": [
                {
                    "id": "/foo",
                    "apps": [],
                    "groups": [
                        {
                            "id": "/foo/bar",
                            "apps": [],
                            "groups": [{"id": "/foo/bar/baz"}]
                        },
                    ]
                },
                {
                    "id": "/foo2",
                    "apps": [],
                    "groups": [],

                },
            ],
            "apps": []
        }
        group = AsgardAppGroup(MarathonGroup.from_json(data))
        self.assertEqual(group.id, "/")
        expected_all_group_ids = ["/", "/foo", "/foo/bar", "/foo/bar/baz", "/foo2"]
        returned_groups = list(group.iterate_groups())
        self.assertEqual(expected_all_group_ids, [g.id for g in returned_groups])

    def test_iterate_group_apps(self):
        data = {
            "id": "/",
            "groups": [
                {
                    "id": "/foo",
                    "apps": [
                        {"id": "/foo/app0"},
                        {"id": "/foo/app1"},
                    ],
                    "groups": [
                        {
                            "id": "/foo/bar",
                            "apps": [],
                            "groups": [
                                {
                                    "id": "/foo/bar/baz",
                                    "apps": [
                                        {"id": "/foo/bar/baz/app0"},
                                        {"id": "/foo/bar/baz/app1"},
                                    ]
                                }
                            ]
                        },
                    ]
                },
            ],
            "apps": [
                {"id": "/app0"},
                {"id": "/app1"}
            ]
        }
        group = AsgardAppGroup(MarathonGroup.from_json(data))
        self.assertEqual(group.id, "/")
        expected_all_apps_ids = ["/app0", "/app1", "/foo/app0", "/foo/app1", "/foo/bar/baz/app0", "/foo/bar/baz/app1"]
        returned_apps = list(group.iterate_apps())
        self.assertEqual(expected_all_apps_ids, [g.id for g in returned_apps])

    def test_modify_some_apps(self):
        data = {
            "id": "/",
            "apps": [
                {"id": "/foo"},
                {"id": "/bla"},
            ],
        }
        group = AsgardAppGroup(MarathonGroup.from_json(data))
        apps = list(group.iterate_apps())
        apps[0].id = "/foo0"
        apps[1].id = "/bla0"

        apps_modified = list(group.iterate_apps())
        self.assertEqual(["/foo0", "/bla0"], [app.id for app in apps_modified])

