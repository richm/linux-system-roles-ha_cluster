# -*- coding: utf-8 -*-

# Copyright (C) 2024 Red Hat, Inc.
# Author: Tomas Jelinek <tojeline@redhat.com>
# SPDX-License-Identifier: MIT

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import sys
from importlib import import_module
from typing import Any, Dict
from unittest import TestCase

sys.modules["ansible.module_utils.ha_cluster_lsr"] = import_module(
    "ha_cluster_lsr"
)

from ha_cluster_lsr.info import exporter


class DictToNvList(TestCase):
    # pylint: disable=protected-access
    def test_no_item(self) -> None:
        self.assertEqual(
            exporter._dict_to_nv_list(dict()),
            [],
        )

    def test_one_item(self) -> None:
        self.assertEqual(
            exporter._dict_to_nv_list(dict(one="1")),
            [dict(name="one", value="1")],
        )

    def test_two_items(self) -> None:
        self.assertEqual(
            exporter._dict_to_nv_list(dict(one="1", two="2")),
            [dict(name="one", value="1"), dict(name="two", value="2")],
        )


class ExportStartOnBoot(TestCase):
    def test_main(self) -> None:
        self.assertFalse(exporter.export_start_on_boot(False, False))
        self.assertTrue(exporter.export_start_on_boot(False, True))
        self.assertTrue(exporter.export_start_on_boot(True, False))
        self.assertTrue(exporter.export_start_on_boot(True, True))


class ExportCorosyncClusterName(TestCase):
    maxDiff = None

    def test_missing_key(self) -> None:
        corosync_data: Dict[str, Any] = dict()
        with self.assertRaises(exporter.JsonMissingKey) as cm:
            exporter.export_corosync_cluster_name(corosync_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=corosync_data,
                key="cluster_name",
                data_desc="corosync configuration",
            ),
        )

    def test_minimal(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            cluster_name="my-cluster",
        )
        role_data = exporter.export_corosync_cluster_name(corosync_data)
        self.assertEqual(role_data, "my-cluster")


class ExportCorosyncTransport(TestCase):
    maxDiff = None

    def assert_missing_key(
        self, corosync_data: Dict[str, Any], key: str
    ) -> None:
        with self.assertRaises(exporter.JsonMissingKey) as cm:
            exporter.export_corosync_transport(corosync_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=corosync_data, key=key, data_desc="corosync configuration"
            ),
        )

    def test_missing_key(self) -> None:
        self.assert_missing_key(
            dict(),
            "transport",
        )
        self.assert_missing_key(
            dict(
                transport="x",
            ),
            "transport_options",
        )
        self.assert_missing_key(
            dict(
                transport="x",
                transport_options=dict(),
            ),
            "links_options",
        )
        self.assert_missing_key(
            dict(
                transport="x",
                transport_options=dict(),
                links_options=dict(),
            ),
            "compression_options",
        )
        self.assert_missing_key(
            dict(
                transport="x",
                transport_options=dict(),
                links_options=dict(),
                compression_options=dict(),
            ),
            "crypto_options",
        )

    def test_minimal(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            transport="KNET",
            transport_options=dict(),
            links_options=dict(),
            compression_options=dict(),
            crypto_options=dict(),
        )
        role_data = exporter.export_corosync_transport(corosync_data)
        self.assertEqual(role_data, dict(type="knet"))

    def test_simple_options_mirroring(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            transport="KNET",
            transport_options=dict(transport1="c", transport2="d"),
            compression_options=dict(compression1="e", compression2="f"),
            crypto_options=dict(crypto1="g", crypto2="h"),
            links_options=dict(),
        )
        role_data = exporter.export_corosync_transport(corosync_data)
        self.assertEqual(
            role_data,
            dict(
                type="knet",
                options=[
                    dict(name="transport1", value="c"),
                    dict(name="transport2", value="d"),
                ],
                compression=[
                    dict(name="compression1", value="e"),
                    dict(name="compression2", value="f"),
                ],
                crypto=[
                    dict(name="crypto1", value="g"),
                    dict(name="crypto2", value="h"),
                ],
            ),
        )

    def test_one_link(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            transport="KNET",
            transport_options=dict(),
            links_options={"0": dict(name1="value1", name2="value2")},
            compression_options=dict(),
            crypto_options=dict(),
        )
        role_data = exporter.export_corosync_transport(corosync_data)
        self.assertEqual(
            role_data,
            dict(
                type="knet",
                links=[
                    [
                        dict(name="name1", value="value1"),
                        dict(name="name2", value="value2"),
                    ]
                ],
            ),
        )

    def test_more_links(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            transport="KNET",
            transport_options=dict(),
            links_options={
                "0": dict(linknumber="0", name0="value0"),
                "7": dict(linknumber="7", name7="value7"),
                "3": dict(linknumber="3", name3="value3"),
            },
            compression_options=dict(),
            crypto_options=dict(),
        )
        role_data = exporter.export_corosync_transport(corosync_data)
        self.assertEqual(
            role_data,
            dict(
                type="knet",
                links=[
                    [
                        dict(name="linknumber", value="0"),
                        dict(name="name0", value="value0"),
                    ],
                    [
                        dict(name="linknumber", value="7"),
                        dict(name="name7", value="value7"),
                    ],
                    [
                        dict(name="linknumber", value="3"),
                        dict(name="name3", value="value3"),
                    ],
                ],
            ),
        )


class ExportCorosyncTotem(TestCase):
    maxDiff = None

    def test_missing_key(self) -> None:
        corosync_data: Dict[str, Any] = dict()
        with self.assertRaises(exporter.JsonMissingKey) as cm:
            exporter.export_corosync_totem(corosync_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=corosync_data,
                key="totem_options",
                data_desc="corosync configuration",
            ),
        )

    def test_minimal(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            totem_options=dict(),
        )
        role_data = exporter.export_corosync_totem(corosync_data)
        self.assertEqual(role_data, dict())

    def test_simple_options_mirroring(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            totem_options=dict(totem1="a", totem2="b"),
        )
        role_data = exporter.export_corosync_totem(corosync_data)
        self.assertEqual(
            role_data,
            dict(
                options=[
                    dict(name="totem1", value="a"),
                    dict(name="totem2", value="b"),
                ],
            ),
        )


class ExportCorosyncQuorum(TestCase):
    maxDiff = None

    def test_missing_key(self) -> None:
        corosync_data: Dict[str, Any] = dict()
        with self.assertRaises(exporter.JsonMissingKey) as cm:
            exporter.export_corosync_quorum(corosync_data)
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=corosync_data,
                key="quorum_options",
                data_desc="corosync configuration",
            ),
        )

    def test_minimal(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            quorum_options=dict(),
        )
        role_data = exporter.export_corosync_quorum(corosync_data)
        self.assertEqual(role_data, dict())

    def test_simple_options_mirroring(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            quorum_options=dict(quorum1="i", quorum2="j"),
        )
        role_data = exporter.export_corosync_quorum(corosync_data)
        self.assertEqual(
            role_data,
            dict(
                options=[
                    dict(name="quorum1", value="i"),
                    dict(name="quorum2", value="j"),
                ],
            ),
        )


class ExportClusterNodes(TestCase):
    maxDiff = None

    def assert_missing_node_key(
        self, corosync_data: Dict[str, Any], key: str, index: int = 0
    ) -> None:
        with self.assertRaises(exporter.JsonMissingKey) as cm:
            exporter.export_cluster_nodes(corosync_data, {})
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=corosync_data,
                key=key,
                data_desc=f"corosync configuration for node on index {index}",
            ),
        )

    def test_missing_key(self) -> None:
        corosync_data: Dict[str, Any] = dict()
        with self.assertRaises(exporter.JsonMissingKey) as cm:
            exporter.export_cluster_nodes(corosync_data, {})
        self.assertEqual(
            cm.exception.kwargs,
            dict(
                data=corosync_data,
                key="nodes",
                data_desc="corosync configuration",
            ),
        )

    def test_no_nodes(self) -> None:
        self.assertEqual(
            exporter.export_cluster_nodes(dict(nodes=[]), {}),
            [],
        )

    def test_corosync_nodes_missing_keys(self) -> None:
        corosync_data: Dict[str, Any] = dict(nodes=[dict()])
        self.assert_missing_node_key(corosync_data, "name")

        corosync_data = dict(nodes=[dict(name="nodename")])
        self.assert_missing_node_key(corosync_data, "addrs")

        corosync_data = dict(nodes=[dict(name="nodename", addrs=[dict()])])
        self.assert_missing_node_key(corosync_data, "link")

        corosync_data = dict(
            nodes=[dict(name="nodename", addrs=[dict(link="0")])]
        )
        self.assert_missing_node_key(corosync_data, "addr")

        corosync_data = dict(
            nodes=[
                dict(name="nodename", addrs=[dict(link="0", addr="addr1")]),
                dict(name="node2"),
            ]
        )
        self.assert_missing_node_key(corosync_data, "addrs", 1)

    def test_corosync_nodes_one_link(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            nodes=[
                dict(
                    name="node1",
                    nodeid=1,
                    addrs=[dict(addr="node1addr", link="0", type="IPv4")],
                ),
                dict(
                    name="node2",
                    nodeid=2,
                    addrs=[dict(addr="node2addr", link="0", type="FQDN")],
                ),
            ]
        )
        role_data = exporter.export_cluster_nodes(corosync_data, {})
        self.assertEqual(
            role_data,
            [
                dict(node_name="node1", corosync_addresses=["node1addr"]),
                dict(node_name="node2", corosync_addresses=["node2addr"]),
            ],
        )

    def test_corosync_nodes_multiple_links(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            nodes=[
                dict(
                    name="node1",
                    nodeid=1,
                    addrs=[
                        dict(addr="node1addr1", link="0", type="IPv4"),
                        dict(addr="node1addr2", link="1", type="IPv6"),
                    ],
                ),
                dict(
                    name="node2",
                    nodeid=2,
                    addrs=[
                        dict(addr="node2addr1", link="0", type="IPv4"),
                        dict(addr="node2addr2", link="1", type="IPv6"),
                    ],
                ),
            ]
        )
        role_data = exporter.export_cluster_nodes(corosync_data, {})
        self.assertEqual(
            role_data,
            [
                dict(
                    node_name="node1",
                    corosync_addresses=["node1addr1", "node1addr2"],
                ),
                dict(
                    node_name="node2",
                    corosync_addresses=["node2addr1", "node2addr2"],
                ),
            ],
        )

    def test_corosync_nodes_no_address(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            nodes=[
                dict(
                    name="node1",
                    nodeid=1,
                    addrs=[],
                ),
            ]
        )
        role_data = exporter.export_cluster_nodes(corosync_data, {})
        self.assertEqual(
            role_data,
            [
                dict(node_name="node1", corosync_addresses=[]),
            ],
        )

    def test_pcs_nodes_no_cluster_nodes(self) -> None:
        corosync_data: Dict[str, Any] = dict(nodes=[])
        pcs_data = dict(node1="node1A")
        role_data = exporter.export_cluster_nodes(corosync_data, pcs_data)
        self.assertEqual(
            role_data,
            [],
        )

    def test_pcs_nodes(self) -> None:
        corosync_data: Dict[str, Any] = dict(
            nodes=[
                dict(
                    name="node1",
                    nodeid=1,
                    addrs=[dict(addr="node1addr", link="0", type="FQDN")],
                ),
                dict(
                    name="node2",
                    nodeid=2,
                    addrs=[dict(addr="node2addr", link="0", type="FQDN")],
                ),
            ]
        )
        pcs_data = dict(node1="node1A", node3="node3A")
        role_data = exporter.export_cluster_nodes(corosync_data, pcs_data)
        self.assertEqual(
            role_data,
            [
                dict(
                    node_name="node1",
                    corosync_addresses=["node1addr"],
                    pcs_address="node1A",
                ),
                dict(
                    node_name="node2",
                    corosync_addresses=["node2addr"],
                ),
            ],
        )
