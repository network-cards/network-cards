#!/usr/bin/env python
# -*- coding: utf-8 -*-

# network_cards.py
# Jim Bagrow
# Last Modified: 2022-09-27

import json
import random
import pprint
from collections import OrderedDict
import numpy as np
import pandas as pd
import networkx as nx
from .format_helpers import save_to_buffer, draw_frame_border, tex_escape


class NetworkCard():
    """Base class for Network Cards. Network cards are semi-standardized tables
    summarizing network data. They consist of three panels, in order:

    1. Overall Information
    2. Structural Information
    3. Metainformation

    Each panel contains named fields describing attributes of the network. Here
    is an example Network Card (w/o footnotes):

                        Name  Experiment A-1
                        Kind  Undirected, weighted
                   Nodes are  Survey participants
                   Links are  Self-reported social ties
            Link weights are  Number of contacts per day
              Considerations  Data gathered for a two-week period

             Number of nodes  50
             Number of links  34
                      Degree  1.4 [0, 6]
                  Clustering  0.0
                   Connected  18 components [44.0%% in largest]
              Component size  2.8 [1, 22]
                    Diameter  N/A
Largest component's diameter  0
      Assortativity (degree)  -0.012048

               Node metadata  Age, gender
               Link metadata  Communication medium (phone or email)
            Date of creation  N/A
     Data generating process  Field survey
                      Ethics  All participants gave informed consent
                     Funding  N/A
                    Citation  N/A
                      Access  https://example.org/data
    """
    _null_string = ""

    def __init__(self, graph, initialize=True):
        """Initialize a network card for `graph`.
        """
        self.graph = graph
        self.D_overall = {}
        self.D_structr = {}
        self.D_metainf = {}
        self._panel_names = ["Overall", "Structure", "Metainformation"]

        if initialize:
            self.update_overall(self.label_name())
            self.update_overall(self.label_kind())
            self.update_overall("Nodes are")
            self.update_overall("Links are")
            if nx.is_weighted(self.graph):
                self.update_overall("Link weights are")
            self.update_overall("Considerations")

            self.update_structure(self.label_nodes())
            self.update_structure(self.label_links())
            if nx.is_directed(self.graph):
                self.update_structure(self.label_bidirectional_links())
            self.update_structure(self.label_degree() )
            self.update_structure(self.label_clustering())
            self.update_structure(self.label_connected())
            self.update_structure(self.label_assort())

            self.update_metainfo("Node metadata")
            self.update_metainfo("Link metadata")
            self.update_metainfo("Date of creation")
            self.update_metainfo("Data generating process")
            self.update_metainfo("Ethics")
            self.update_metainfo("Funding")
            self.update_metainfo("Citation")
            self.update_metainfo("Access")

        self._sizes()

    def _str_labeler(self, label, func):
        return {label: func(self.graph)}

    def label_name(self, unnamed=""):
        """Get entry for network's name. Intended for card's overall panel.

        Network's name is inferred from networkx graph.name attribute. Use
        `unnamed` (default: "") if no name given.

        See also: omit_label.
        """
        s = self.graph.name
        s = unnamed if not s else s
        return {"Name": s}

    def label_nodes(self):
        """Get entry for network's number of nodes. Intended for card's
        structure panel.
        """
        return self._str_labeler("Number of nodes", nx.number_of_nodes)

    def label_connected(self):
        """Get entries describing whether network is connected. Intended for
        card's structure panel.

        For undirected networks:
            If connected, report the network's diameter. If not connected,
            report the number of connected components, a summary of the
            component size distribution, and the largest connected component's
            diameter.

        For directed networks:
            If strongly connected, report network's diameter. If weakly
            connected or not connected, report as such.
        """
        if self.graph.is_directed():
            return self._label_connected_directed()
        return self._label_connected_undirected()

    def _label_connected_undirected(self):
        """See label_connected."""
        ncc = nx.number_connected_components(self.graph)
        if ncc == 1:
            return {"Connected": "Yes", 'Diameter': nx.diameter(self.graph)}
        comps = sorted(nx.connected_components(self.graph), key=len, reverse=True)
        sizes = list(map(len,comps))
        d = {"Connected":
             f"{ncc} components [{max(sizes)/len(self.graph):.2%} in largest]"
             }
        d.update(self.summarize_distribution(sizes, label='Component size'))
        d['Diameter'] = "n/a" # self._null_string
        d["Largest component's diameter"] = nx.diameter(self.graph.subgraph(comps[0]))
        return d

    def _label_connected_directed(self):
        """See label_connected."""
        if nx.is_strongly_connected(self.graph):
            return {"Connected": "Strongly connected", 'Diameter': nx.diameter(self.graph)}
        if nx.is_weakly_connected(self.graph):
            return {"Connected": "Weakly connected"}
        return {"Connected": "Disconnected"}

    def label_links(self):
        """Get entry for network's number of links. Intended for card's
        structure panel.
        """
        nsl = nx.number_of_selfloops(self.graph)
        if nsl > 0:
            m = nx.number_of_edges(self.graph)
            lbl = 'self-loop' if nsl == 1 else 'self-loops'
            return {'Number of links': f"{m} ({nsl} {lbl})"}
        return self._str_labeler("Number of links", nx.number_of_edges)

    def label_bidirectional_links(self):
        """Get entry for network's proportion (%) of bidirectional link.
        Intended for card's structure panel. Intended for directed networks.

        A bidirectional link is one where both (i,j) and (j,i) links exist.
        """
        num_directed_links = self.graph.number_of_edges()
        undirected_links = {tuple(sorted(ij)) for ij in self.graph.edges()}
        num_bidirectional_links = num_directed_links - len(undirected_links)

        return {"--- Bidirectional links" : f"{100*num_bidirectional_links/num_directed_links:.3g}%" }

    def label_degree(self):
        """Get entry summarizing network's degree distribution. Intended for
        card's structure panel.

        If undirected, report summary of network's degree distribution.

        If directed, report summary of network's undirected degree
        distribution, in-degree, and out-degree distributions.
        """
        if self.graph.is_directed():
            return self._label_degree_directed()
        return self._label_degree_undirected()

    def _label_degree_undirected(self):
        """See label_degree."""
        degs = [k for _,k in self.graph.degree()]
        return self.summarize_distribution(degs, label='Degree')

    def _label_degree_directed(self):
        """See label_degree."""
        degs_un = [k for _,k in self.graph.degree()]
        degs_in = [k for _,k in self.graph.in_degree()] # mean in/out degree same

        field = self.summarize_distribution(degs_in, label='Degree (in/out)')
        field.update(self.summarize_distribution(degs_un, label='Degree'))
        entry, note = field['Degree']
        field['Degree'] = (entry, "Undirected.", note)
        return field

    def label_assort(self):
        """Get entry for network's degree assortativity. Intended for card's
        structure panel.
        """
        return self._str_labeler("Assortativity (degree)",
                                 nx.degree_assortativity_coefficient)

    def label_clustering(self):
        """Get entry for network's average clustering. Intended for card's
        structure panel.
        """
        try:
            return self._str_labeler("Clustering", nx.average_clustering)
        except ZeroDivisionError:
            return {"Clustering": 0}# or na for empty graph?

    def label_kind(self, weight_name='weight'):
        """Infer a list of properties the graph has, undirected or direct,
        weighted or unweighted.  Checks if graph is weighted by looking for a
        network edge attribute named `weight_name`.
        """

        attributes = []
        #if nx.is_bipartite(graph):         # bipartite by chance or by design?
        #    attributes.append("bipartite") #
        #if not nx.is_connected(graph):
        #    attributes.append("disconnected")
        if nx.is_directed(self.graph):
            attributes.append('directed')
        else:
            attributes.append('undirected')
        if nx.is_weighted(self.graph, weight=weight_name):
            if nx.is_negatively_weighted(self.graph, weight=weight_name):
                attributes.append("weighted (negatively)")
            else:
                attributes.append("weighted")
        else:
            attributes.append("unweighted")

        return {"Kind": ", ".join(sorted(attributes)).capitalize()}

    def update_overall(self, data, value=None):
        """Insert or replace entries in the network card's 'overall' panel.
        Entries can be passed as {field:entry} dicts, or as field, entry
        argument pair. Example:

        >>> nc = NetworkCard(graph)
        >>> nc.update_overall({"Nodes are": "Platform users"})
        >>> nc.update_overall("Nodes are", "Platform users")
        """
        if value:
            data = {data: value}
        self._update(data, self.D_overall)

    def update_structure(self,data, value=None):
        """Insert or replace entries in the network card's 'structure' panel.
        See update_overall for details.
        """
        if value:
            data = {data: value}
        self._update(data, self.D_structr)

    def update_metainfo(self,data, value=None):
        """Insert or replace entries in the network card's 'metainfo' panel.
        See update_overall for details.
        """
        if value:
            data = {data: value}
        self._update(data, self.D_metainf)

    def _update(self, data, dest):
        if isinstance(data,str):
            data = {data:self._null_string}
        dest.update(data)
        self._sizes()

    def remove_overall(self, field):
        """Remove a field from network card's overall info panel. No change if
        field is not present.
        """
        self._remove(field, self.D_overall)

    def remove_structure(self, field):
        """Remove a field from network card's structure panel. No change if field
        is not present.
        """
        self._remove(field, self.D_structr)

    def remove_metainfo(self, field):
        """Remove a field from network card's metainfo panel. No change if field
        is not present.
        """
        self._remove(field, self.D_metainf)

    def _remove(self, field, dest):
        """Remove field from dest and update sizes."""
        dest.pop(field)
        self._sizes()

    def add_footnote(self, field, note):
        """Add footnote to field. This will use the first panel containing
        `field`. If you want to control the panel manually, use
        `add_footnote_PANEL` instead, where PANEL in [overall, structure,
        metainfo].
        """
        if field in self.D_overall:
            self.add_footnote_overall(field, note)
        elif field in self.D_structr:
            self.add_footnote_structure(field, note)
        elif field in self.D_metainf:
            self.add_footnote_metainfo(field, note)
        else:
            raise KeyError(f"Field '{field}' not found in any panel.")

    def add_footnote_overall(self, field, note):
        """Add footnote to `field`'s entry in the overall panel.
        Raise KeyError if field not present.
        """
        self._add_footnote(field, note, self.D_overall)

    def add_footnote_structure(self, field, note):
        """Add footnote to `field`'s entry in the structure panel.
        Raise KeyError if field not present.
        """
        self._add_footnote(field, note, self.D_structr)

    def add_footnote_metainfo(self, field, note):
        """Add footnote to `field`'s entry in the metainformation panel.
        Raise KeyError if field not present.
        """
        self._add_footnote(field, note, self.D_metainf)

    def _add_footnote(self, field, note, dest):
        """Add footnote to `field`'s entry in `dest`."""
        try:
            entry = dest[field]
            if isinstance(entry, (tuple,list)):
                entry = list(entry)
            else:
                entry = [entry]
            entry.append(note)
            dest[field] = tuple(entry)
        except KeyError as e:
            raise KeyError(f"Field {field} not found in specified dict {dest}", e) from e

    def __repr__(self):
        s = self._series()

        # clean up footnotes:
        fields = list(s['index'])
        list_notes = list(s[1])
        new_fields = []
        num = 1
        n2num = {}
        for f,note in zip(fields,list_notes):
            if note is None: # blanks do nothing
                new_fields.append(f)
                continue
            marks = ""
            for n in note:
                try:
                    marks += f"^{n2num[n]}"
                except KeyError:
                    marks += f"^{num}" # do NOT modify first occurrence
                    n2num[n] = num
                    num += 1
            new_fields.append(f + marks)
        s['index'] = new_fields
        del s[1]
        notes = "\n".join([f"^{num}: {n}" for n, num in n2num.items()])

        txt = s.to_string(float_format='{:.3g}'.format,
                          index=False, header=False
                          )
        return "\n\n".join([txt, notes])

    def _join_dicts(self):
        """Return dict joining the overall dict, structure dict, metainf dict,
        and footnote dict (in order).
        """
        self._sizes()
        this_dict = {}
        this_dict.update(self.D_overall)
        this_dict.update(self.D_structr)
        this_dict.update(self.D_metainf)
        return this_dict

    def summarize_distribution(self, values, label=None):
        """Build string of mean of values and (for now) min and max.

        TODO: handle median, percentiles?
        """
        label = "" if label is None else label
        lbl = f"{label}".strip() # footnote form

        if len(values) <= 5:
            s = str(list(sorted(values, reverse=True)))
            return {lbl: s}

        try:
            s = f"{np.mean(values):g} [{min(values)}, {max(values)}]"
        except ValueError:
            return {lbl:self._null_string}
        ftext = r"Distributions summarized with average [min, max]."
        #ftext = r"Distributions summarized with Median [5, 95 percentile]."
        return {lbl: (s,ftext)}

    def _series(self):
        """Combine Network Card dicts, convert to pandas series and return."""
        # put footnotes into their own column
        D = self._join_dicts()
        for field,entry in D.items():
            if not isinstance(entry, (tuple,list)):
                D[field] = (entry,)
        s = pd.Series(D).reset_index()
        s[1] = s[0].apply(lambda x:x[1:] if len(x)>1 else None)
        s[0] = s[0].apply(lambda x:x[0])
        return s

    def clear(self, value="", keep_notes=False):
        """Clear all entries from network card while retaining the fields
        themselves. Useful for creating a blank card template.
        """
        panels = [self.D_overall, self.D_structr, self.D_metainf]
        for panel in panels:
            for field in panel:
                entry = panel[field]
                if keep_notes and isinstance(entry, (tuple,list)):
                    entry = list(entry)
                    entry[0] = value
                    panel[field] = entry
                else:
                    panel[field] = value

    def to_frame(self):
        """Convert Network Card to Pandas DataFrame.

        Format is one row per entry with columns Panel, Field, Value, and Note.
        Note is empty string if Value has no footnote.
        """
        L = []
        panels = [self.D_overall, self.D_structr, self.D_metainf]
        for n,d in zip(self._panel_names, panels):
            for fl,va in d.items():
                if isinstance(va, (tuple,list)):
                    ft = va[1:]
                    va = va[0]
                else:
                    va, ft = va, ""
                L.append({'Panel':n, "Field":fl, "Value":va, "Note":ft})
        return pd.DataFrame(L)

    def _sizes(self):
        self._n_ov_ = len(self.D_overall)
        self._n_st_ = len(self.D_structr)
        self._n_mi_ = len(self.D_metainf)

        self._n_ov_st_    = self._n_ov_ + self._n_st_
        self._n_ov_st_mi_ = self._n_ov_ + self._n_st_ + self._n_mi_

    def to_latex(self, buf=None, max_width=None):
        """Save Network Card to LaTeX format. Write to `buf` (or return as string
        if buf is None).

        max_width: width in cm for the right column.
        """
        s = self._series()

        # clean up footnotes:
        fields = list(s['index'])
        list_notes = list(s[1])
        new_fields = []
        num = 0
        n2num = {}
        for f,note in zip(fields,list_notes):
            if note is None: # blanks do nothing
                new_fields.append(f)
                continue
            marks = []
            for n in note:
                try:
                    marks.append( f"\\textsuperscript{{\\ref{{foot{n2num[n]}}}}}" )
                except KeyError:
                    marks.append( f"\\tablefootnote{{\\label{{foot{num}}}{n}}}" ) # do NOT modify first occurrence
                    n2num[n] = num
                    num += 1
            marks = r"\textsuperscript{,}".join(marks) # footnotes 1,2 not 1 2
            new_fields.append(f + marks)
        s['index'] = new_fields
        del s[1]

        column_format = None
        if max_width is not None:
            column_format=f"lp{{{max_width}cm}}"

        s[0] = s[0].apply(tex_escape)
        ltx = s.style.hide(axis=0).hide(axis=1).format(precision=4).to_latex(hrules=True, column_format=column_format).splitlines()
        ltx.pop(2) # remove midrule added by pandas to go under (hidden) column names
        ltx.insert(self._n_ov_st_   +2, r'\midrule') # separator before metainfo panel
        ltx.insert(self._n_ov_      +2, r'\midrule') # separator before structure panel
        ltx.append(r"% footnotes require tablefootnote package (put \usepackage{tablefootnote} in preamble)")
        return save_to_buffer("\n".join(ltx), buf)

    def to_excel(self, filename, formatted=True):
        """Save Network Card to Excel (xlsx) format."""
        s = self._series()

        # clean up footnotes:
        fields = list(s['index'])
        list_notes = list(s[1])
        new_fields = []
        num = 1
        n2num = {}
        for _,(f,note) in enumerate(zip(fields,list_notes)):
            if note is None: # blanks do nothing
                new_fields.append(f)
                continue
            marks = []
            for n in note:
                try:
                    marks.append( f"{n2num[n]}" )
                except KeyError:
                    marks.append( f"{num}" ) # do NOT modify first occurrence
                    n2num[n] = num
                    num += 1
            marks = ",".join(sorted(marks))
            new_fields.append(f + f" ({marks})" if marks else f)
        values = list(s[0])
        notes = [f"{num}: {n}" for n, num in n2num.items()]
        values.extend([""]*len(notes))
        new_fields.extend(notes)
        s = pd.Series( dict(zip(new_fields, values)) ).reset_index()

        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        s.to_excel(writer, sheet_name='Sheet1', float_format='%.3g',
                   header=False, index=False)

        if formatted:
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            worksheet.hide_gridlines(2)
            label_fmt = workbook.add_format({'text_wrap': False, 'align':'left'})
            field_fmt = workbook.add_format({'text_wrap': True,  'align':'left'})
            worksheet.set_column('A:A', 19, label_fmt)
            worksheet.set_column('B:B', 35, field_fmt)
            worksheet.set_zoom(150) # Am I old?

            draw_frame_border(workbook, worksheet, 0,             0, self._n_ov_,2)
            draw_frame_border(workbook, worksheet, self._n_ov_,   0, self._n_st_,2)
            draw_frame_border(workbook, worksheet, self._n_ov_st_,0, self._n_mi_,2)

        writer.save()

    def to_dict(self):
        """Convert network card to dictionary of dictionaries, one dictionary
        per panel.
        """
        obj = {'overall'   : self.D_overall,
               'structure' : self.D_structr,
               'metainfo'  : self.D_metainf,
               }
        return obj

    def to_json(self, buf=None):
        """Save network card to dictionary of dictionaries, one dictionary per
        panel.  Write to `buf` (or return as string if buf is None).
        """
        return save_to_buffer( json.dumps(self.to_dict()), buf )

    def pprint(self):
        """Pretty-print the dict representation of the network card."""
        pprint.pprint(self.to_dict(), sort_dicts=False)


class NetworkMultiCard():
    _null_string = ""

    def __init__(self, cards):
        """Combine cards into a Network MultiCard.
        """
        self.num_networks = len(cards)
        self.D = pd.DataFrame(columns=['Panel', 'Field'])
        for i,card in enumerate(cards):
            this_D = card.to_frame()
            this_D.rename(columns={'Value': f'Value_{i}', 'Note': f"Note_{i}"},
                          inplace=True)
            self._merge_onto(this_D)
        self._merge_all_notes()

        # ensure all panels are in right order:
        D_ov = self.D[self.D['Panel'] == 'Overall']
        D_st = self.D[self.D['Panel'] == 'Structure']
        D_mi = self.D[self.D['Panel'] == 'Metainformation']
        self.D = pd.concat( [D_ov, D_st, D_mi]).reset_index(drop=True)

    def _merge_onto(self, frame):
        """Merge frame into the multicard.
        """
        self.D = pd.merge(self.D, frame, how='outer', on=["Panel", "Field"])

    def _merge_all_notes(self):
        """Take every separate card's footnote column and merge into a single note column."""
        notes_cols = [c for c in self.D if c.startswith('Note_')]
        new_notes = []
        for _, row in self.D[notes_cols].fillna("").iterrows():
            new_notes.append( set(self._flatten(row.tolist())) -{""} )

        self.D["Note"] = new_notes
        self.D.drop(notes_cols, axis=1, inplace=True)

    def _flatten(self, items, seqtypes=(list, tuple)):
        try:
            for i, x in enumerate(items):
                while isinstance(x, seqtypes):
                    items[i:i+1] = x
                    x = items[i]
        except IndexError:
            pass
        return items

    def __repr__(self):
        show_frame = self.D.drop("Panel", axis=1).fillna(self._null_string)

        # clean up footnotes:
        fields = list(show_frame['Field'])
        list_notes = list(show_frame['Note'])
        new_fields = []
        num = 1
        n2num = {}
        for f,note in zip(fields,list_notes):
            if note is None or note == "": # blanks do nothing
                new_fields.append(f)
                continue
            marks = ""
            for n in note:
                try:
                    marks += f"^{n2num[n]}"
                except KeyError:
                    marks += f"^{num}" # do NOT modify first occurrence
                    n2num[n] = num
                    num += 1
            new_fields.append(f + marks)
        show_frame['Field'] = new_fields
        show_frame.drop('Note', axis=1, inplace=True)
        notes = "\n".join([f"^{num}: {n}" for n, num in n2num.items()])

        txt = show_frame.to_string(float_format='{:.3g}'.format,
                          index=False, header=False
                          )
        return "\n\n".join([txt, notes])

    def show_fields(self, verbose=True):
        """Helper to show all fields and their indices in the multicard. Useful
        when you want to manually reorder the fields using the swap_two_rows
        method.
        """
        for panel in ['Overall', "Structure", "Metainformation"]:
            if verbose:
                print(f"{panel}:")
            print(self.D[self.D['Panel']==panel]['Field'].to_string(name=False, dtype=False))
            if verbose:
                print("")

    def get_index(self):
        """List of row numbers for the multicard."""
        return self.D.index.tolist()

    def swap_two_rows(self, pos1, pos2):
        """Interchange rows at pos1 and pos2 in the multicard. Use show_fields()
        to see row positions to use.
        """
        idx = self.get_index()
        idx[pos2], idx[pos1] = idx[pos1], idx[pos2]
        self.D = self.D.reindex(index=idx).reset_index(drop=True)

    def to_latex(self, buf=None, col_width=2.5):
        """Save MultiCard to LaTeX format. Write to `buf` (or return as string
        if buf is None).

        `col_width` is the width of each network column in cm.

        Use inside a .tex document with \\include{FILENAME} inside table
        environment.
        """
        show_frame = self.D.drop("Panel", axis=1).fillna(self._null_string)
        fields = list(show_frame['Field'])
        list_notes = list(show_frame["Note"])
        new_fields = []
        num = 0
        n2num = {}
        for f,note in zip(fields,list_notes):
            if note is None or note == "": # blanks do nothing
                new_fields.append(f)
                continue
            marks = []
            for n in note:
                try:
                    marks.append( f"\\textsuperscript{{\\ref{{foot{n2num[n]}}}}}" )
                except KeyError:
                    marks.append( f"\\tablefootnote{{\\label{{foot{num}}}{n}}}" ) # do NOT modify first occurrence
                    n2num[n] = num
                    num += 1
            marks = r"\textsuperscript{,}".join(marks) # footnotes 1,2 not 1 2
            new_fields.append(f + marks)
        show_frame['Field'] = new_fields
        show_frame.drop('Note', axis=1, inplace=True)

        for c in show_frame.columns:
            if c.startswith("Value"):
                show_frame[c] = show_frame[c].apply(tex_escape)

        nov = len(self.D[self.D['Panel']=='Overall'])
        nst = len(self.D[self.D['Panel']=='Structure'])

        cf = "l" + rf">{{\raggedright\arraybackslash}}p{{{col_width}cm}}"*(len(show_frame.columns)-1)
        ltx = show_frame.style.hide(axis=0).hide(axis=1).format(precision=4).to_latex(hrules=True, column_format=cf).splitlines()

        ltx.pop(2) # remove midrule added by pandas to go under (hidden) column names
        ltx.insert(nov+nst+2, r'\midrule') # separator before metainfo panel
        ltx.insert(nov    +2, r'\midrule') # separator before structure panel
        ltx.append(r"% footnotes require tablefootnote package (put \usepackage{tablefootnote} in preamble)")
        ltx.append(r"% put \usepackage{array} in preamble")
        return save_to_buffer("\n".join(ltx), buf)

    def to_excel(self, filename, formatted=True):
        """Save MultiCard to Excel (xlsx) format."""
        s = self.D.copy()

        # clean up footnotes:
        fields = list(s['Field'])
        list_notes = list(s['Note'])
        new_fields = []
        num = 1
        n2num = {}
        for r,(f,note) in enumerate(zip(fields,list_notes)):
            if note is None or note == "": # blanks do nothing
                new_fields.append(f)
                continue
            marks = []
            for n in note:
                try:
                    marks.append( f"{n2num[n]}" )
                except KeyError:
                    marks.append( f"{num}" ) # do NOT modify first occurrence
                    n2num[n] = num
                    num += 1
            marks = ",".join(sorted(marks))
            new_fields.append(f + f" ({marks})" if marks else f)
        notes = [{'Field':f"{num}: {n}"} for n, num in n2num.items()]
        s['Field'] = new_fields
        s = pd.concat([s, pd.DataFrame(notes)])
        s.drop(['Panel','Note'], axis=1, inplace=True)

        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        s.to_excel(writer, sheet_name='Sheet1', float_format='%.3g',
                   header=False, index=False)

        if formatted:
            nov = len(self.D[self.D['Panel']=='Overall'])
            nst = len(self.D[self.D['Panel']=='Structure'])
            nmi = len(self.D[self.D['Panel']=='Metainformation'])

            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            worksheet.hide_gridlines(2)
            label_fmt = workbook.add_format({'text_wrap': False, 'align':'left'})
            field_fmt = workbook.add_format({'text_wrap': True,  'align':'left'})
            worksheet.set_column('A:A', 19, label_fmt)
            worksheet.set_column('B:'+chr(ord("A")+self.num_networks), 30, field_fmt)
            worksheet.set_zoom(150) # Am I old?

            draw_frame_border(workbook, worksheet, 0,      0, nov,self.num_networks+1)
            draw_frame_border(workbook, worksheet, nov,    0, nst,self.num_networks+1)
            draw_frame_border(workbook, worksheet, nov+nst,0, nmi,self.num_networks+1)

        writer.save()


def read_json(buf, graph):
    """Read json serialized network card. Requires graph."""
    try:
        buf = buf.read()
    except AttributeError:
        pass
    D = json.loads(buf, object_pairs_hook=OrderedDict)
    Card = NetworkCard(graph, initialize=False)
    Card.update_overall(D['overall'])
    Card.update_structure(D['structure'])
    Card.update_metainfo(D['metainfo'])

    return Card


def _align_dicts_ordered(D1, D2, value=""):
    """Make new dicts with same keys inserted in order of appearance."""
    keys_both = set(D1.keys()) | set(D2.keys())
    L1, L2 = list(D1.keys()), list(D2.keys())
    L = []
    for k in keys_both:
        try:
            idx1 = L1.index(k)
        except ValueError:
            idx1 = None
        try:
            idx2 = L2.index(k)
        except ValueError:
            idx2 = None
        print(k, idx1, idx2)

        if idx1 is None:
            idx = 2*idx2
        elif idx2 is None:
            idx = 2*idx1
        else:
            idx = idx1 + idx2 - 0.5
        L.append( (idx, k))
    L.sort()
    #for i,k in L:
    #    print(i,k)
    #print([k for i,k in L])
    L = [k for i,k in L]
    print("***")

    D1_new, D2_new = {}, {}
    for k in L:
        try:
            D1_new[k] = D1[k]
        except KeyError:
            D1_new[k] = value
        try:
            D2_new[k] = D2[k]
        except KeyError:
            D2_new[k] = value
    return D1_new, D2_new


def align_cards(C1, C2):
    """Ensure that any keys in one card are also in the other. Can be used when
    making a multicard with one network per column, but it's a little finicky
    and may be dropped.
    """
    C1.D_overall, C2.D_overall = _align_dicts_ordered(C1.D_overall, C2.D_overall, value=C1._null_string)
    C1.D_structr, C2.D_structr = _align_dicts_ordered(C1.D_structr, C2.D_structr, value=C1._null_string)
    C1.D_metainf, C2.D_metainf = _align_dicts_ordered(C1.D_metainf, C2.D_metainf, value=C1._null_string)

    C1._sizes()
    C2._sizes()


if __name__ == '__main__':

    D = nx.DiGraph()
    D.add_edge(0,1)
    D.add_edge(0,2)
    D.add_edge(2,3)
    D.add_edge(3,2)
    nc = NetworkCard(D)
    print(nc)
    nc.to_latex("test-card.tex")


    G = nx.erdos_renyi_graph(50,0.03)
    G.name = "ER graph 001"
    for (u, v) in G.edges():
        G.edges[u,v]['weight'] = random.randint(0,10)

    NC = NetworkCard(G)
    NC.update_overall({"Link weights are" : "Synthetic - U[0,10]"})
    #print(NC)


    #align_cards(nc,NC)

    #NC.to_latex("test-card.tex")
    #NC.to_excel("fmt-test.xlsx")

    H = nx.barabasi_albert_graph(50,2)
    NC2 = NetworkCard(H)


    NMC = NetworkMultiCard([nc, NC, NC2])
    NMC.swap_two_rows(4,5)
    NMC.to_excel("test-multicard.xlsx")
    NMC.to_latex("test-multicard.tex")
