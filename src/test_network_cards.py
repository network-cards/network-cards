#!/usr/bin/env python
# -*- coding: utf-8 -*-

# tests.py
# Jim Bagrow
# Last Modified: 2022-02-18

import networkx as nx
import network_cards


def test_name_integrate():
    G = nx.Graph()
    G.name = "Graph 01"
    x = network_cards.stringify_dict(network_cards.str_name(G))
    assert x == "Name: Graph 01\n"


def test_kind1_graph_integrate():
    G = nx.erdos_renyi_graph(10,0.9)
    x = network_cards.stringify_dict(network_cards.str_kind(G))
    assert x == "Kind: Undirected, unweighted\n"


def test_kind2_graph_integrate():
    G = nx.erdos_renyi_graph(10,0.0)
    x = network_cards.stringify_dict(network_cards.str_kind(G))
    assert x == "Kind: Disconnected, undirected, unweighted\n"

def test_graph_degrees1():
    G = nx.Graph()
    assert network_cards._graph_degrees(G) == []

def test_graph_degrees2():
    G = nx.Graph()
    G.add_edges_from([(1,2),(1,3)])
    assert network_cards._graph_degrees(G) == [2,1,1]
