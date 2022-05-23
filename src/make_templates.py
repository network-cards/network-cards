#!/usr/bin/env python
# -*- coding: utf-8 -*-

# make_templates.py
# Jim Bagrow
# Last Modified: 2022-05-23

import random
import networkx as nx
import network_cards as nc


def save_template_excel(graph, filename, updates=None):
    card = nc.NetworkCard(graph)
    card.clear(keep_notes=True)
    if updates is not None:
        card.update_structure(*updates)
    card.to_excel(filename+".xlsx")


def save_template_latex(graph, filename, updates=None):
    card = nc.NetworkCard(graph)
    card.clear(keep_notes=True)
    if updates is not None:
        card.update_structure(*updates)
    card.to_latex(filename+".tex")


for connected in ['connected', 'unconnected']:
    p = 0.24 if connected == 'connected' else 0.01

    updates = ("Diameter", "n/a") if connected == 'unconnected' else None

    # undirected, unweighted:   
    G = nx.erdos_renyi_graph(100,p)
    if connected == 'connected':
        assert nx.is_connected(G) == True
    else:
        assert nx.is_connected(G) == False

    for st in [save_template_excel, save_template_latex]:
        st(G, f"../templates/undirected_unweighted_{connected}",
           updates=updates)

    # undirected, weighted:
    G = nx.erdos_renyi_graph(100,p)
    for (u, v) in G.edges():
        G.edges[u,v]['weight'] = random.randint(0,10)
    if connected == 'connected':
        assert nx.is_connected(G) is True
    else:
        assert nx.is_connected(G) is False

    for st in [save_template_excel, save_template_latex]:
        st(G, f"../templates/undirected_weighted_{connected}",
           updates=updates)

# directed, unweighted:
D = nx.DiGraph()
D.add_edge(0,1)
D.add_edge(0,2)
D.add_edge(2,3)
D.add_edge(3,2)
for st in [save_template_excel, save_template_latex]:
    st(D, "../templates/directed_unweighted")

# directed, weighted:
for (u, v) in D.edges():
    D.edges[u,v]['weight'] = random.randint(0,10)
for st in [save_template_excel, save_template_latex]:
    st(D, "../templates/directed_weighted")

