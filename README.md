# Network Cards

A network card is a three-panel tabular summary of a network dataset:

<p align='center'>
<img src='https://raw.githubusercontent.com/network-cards/network-cards/main/network-card-example.png' alt='Example network card for the Zachary Karate Club' width='600'>
</p>

The first panel provides an overall summary of the network, the second summarizes the structure of the network (size, density, connectivity), and the third panel provides additional meta-information, what metadata are associated with nodes and links, how were the data gathered, and so forth.

Network cards are intended to be _concise, readable and flexible_, allowing researchers across fields to quickly read and understand studies involving network datasets. 
We believe that a standard representation is crucial to ensuring that key information associated with network data remains available.

This repository provides [templates](templates/) and a [Python package](#install) to create, update, and export network cards.

Interested in more? Check out [the paper][1].

## Table of Contents

* [Install](#install)
	- [Requirements](#requirements)
* [Example](#example)
* [Citation](#citation)
* [License](#License)


## Install

`pip install network-cards`

#### Requirements

* Python 3.8+
* Networkx
* Pandas




## Example

`Network Cards` provides [fill-in templates](templates/) but you can also generate and save a card programmatically. 
Here's Python code where we load a network from a file and compute the basic card: 

```python
import networkx as nx
import network_cards as nc

G = nx.read_edgelist("karate_club.edgelist")

card = nc.NetworkCard(G)
print(card)
```
This gives:

```text
                   Name                       
                   Kind Undirected, unweighted
              Nodes are                       
              Links are                       
         Considerations                       
        Number of nodes                     34
        Number of links                     78
               Degree^1        4.58824 [1, 17]
             Clustering                  0.571
              Connected                    Yes
               Diameter                      5
 Assortativity (degree)                 -0.476
          Node metadata                       
          Link metadata                       
       Date of creation                       
Data generating process                       
                 Ethics                       
                Funding                       
               Citation                       

^1: Distributions summarized with average [min, max].
```

Unfortunately, few of the important definitions, details or meta-information are computable, so
most of the fields outside the structure panel are blank.
Let's use `update_*` methods to populate the remaining fields ourselves:

```python
card.update_overall("Name", "Zachary Karate Club")
card.update_overall("Nodes are", "Members of club at US university")
card.update_overall("Links are", "Members consistently interacted outside club")
card.update_overall("Considerations", "Heavily used as an example network")

card.update_metainfo({
    "Node metadata":           "None",
    "Link metadata":           "None (original study included eight interaction contexts)",
    "Date of creation":        "1977",
    "Data generating process": "Direct observation of club members during period 1970-72",
    "Funding":                 "None",
    "Citation":                "Zachary (1977)"
    })
```

We used `card.update_overall()` and `card.update_metainfo()` to insert entries into the previous card. 
Entries can be updated one at a time (like we did when updating the overall panel) or a dictionary can be passed to update multiple entries at once.

Now, print the revised card with `print(card)`:

```text
                   Name                                       Zachary Karate Club
                   Kind                                    Undirected, unweighted
              Nodes are                          Members of club at US university
              Links are              Members consistently interacted outside club
         Considerations                        Heavily used as an example network
        Number of nodes                                                        34
        Number of links                                                        78
               Degree^1                                           4.58824 [1, 17]
             Clustering                                                     0.571
              Connected                                                       Yes
               Diameter                                                         5
 Assortativity (degree)                                                    -0.476
          Node metadata                                                      None
          Link metadata None (original study included eight interaction contexts)
       Date of creation                                                      1977
Data generating process  Direct observation of club members during period 1970-72
                 Ethics                                                          
                Funding                                                      None
               Citation                                            Zachary (1977)

^1: Distributions summarized with average [min, max].
```

And we can save to a convenient file format:

```python
card.to_latex("karate-card.tex")
card.to_excel("karate-card.xlsx")
```




## Citation

If you use a Network Card, please cite [our paper][1]:

Bagrow, J., & Ahn, Y. (2022). Network Cards: concise, readable summaries of network data

Here is a bibtex entry ([.bib file](references/citation.bib)):

```bibtex
@unpublished{bagrow2022cards,
	author = {Bagrow, James and Ahn, Yong-Yeol},
	title  = {Network Cards: concise, readable summaries of network data},
	year   = {2022},
}
```

and a .ris entry ([.ris file](references/citation.ris)):

```text
TY  - UNPB
AU  - Bagrow, James
AU  - Ahn, Yong-Yeol
TI  - Network Cards: concise, readable summaries of network data
PY  - 2022
DA  - 2022
ER  - 
```

## License

[BSD-3-Clause](LICENSE) © James Bagrow


[1]: https://arxiv.org/abs/2206.00026 "Network Cards: concise, readable summaries of network data"
