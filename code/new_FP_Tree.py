import numpy as np
from collections import OrderedDict
import csv

from preprocessing import test
import CR_Tree

""" Data structure for FP-Tree """
class FPTNode:
    def __init__(self, attri, count, parent):
        self.attri = attri  # attribute tuple: (col, value)
        self.count = count  # counts of this value for the attribute
        self.parent = parent  # parent node
        self.child = OrderedDict()  # {attri: child node}
        self.link_next = None  # next node with the same column index in the link
        self.labels = {} # {class label: count}

    # Method to display the FP-Tree or conditional FP-Tree as a nested list
    def display_tree_list(self):
        print(self.attri, self.count, end='')
        if len(self.child) > 0:
            print(",[", end='')
        for c in self.child.values():
            print("[", end='')
            # For any children of the node, call the function recursively
            c.display_tree_list()
            if len(c.child) == 0:
                print("]", end='')
        print("]", end='')






"""This function takes the input dataset and scans it once to create the
frequent item dictionary. Once that is created, it deletes any value in the
dictionary which is below the threshold."""


def ordered_F_list(test_data, min_support):
    col_length = len(test_data[0]) - 1
    value_count = []
    for i in range(col_length):
        value_count.append({})
    for case in test_data:
        for i in range(col_length):
            if case[i] in value_count[i]:
                value_count[i][case[i]] += 1
            else:
                value_count[i][case[i]] = 0
    # add attribute values into F_list if their counts >= min_support
    F_list = []
    for i in range(col_length):
        for key, value in value_count[i].items():
            if value >= min_support:
                # [col index, value, count]
                F_list.append([i, key, value])
            # else:
            #     del value_count[i][key]
    # sort by counts in descending order
    F_list = sorted(F_list, key=lambda x: x[2], reverse=True)
    return  F_list, value_count


"""This function scans the database for the second time.
The attribute values in each data case are ordered by F_list.
The ordered data case will be added into the FP-Tree."""


def create_FP_tree(test_data, F_list):
    # FPTNode(attri, count, parent)
    root = FPTNode('Root', 1, None)

    # create empty header table
    header_table = {}

    # add each data case into the FP tree
    for case in test_data:
        ordered_case = []
        for e in F_list:
            if case[e[0]] == e[1]:
                ordered_case.append((e[0], e[1]))
        ordered_case.append(case[-1]) # append the class label
        update_FP_tree(root, ordered_case, header_table)
    return root, header_table


"""This function recursively creates the FP-Tree for each transaction."""


def update_FP_tree(this_node, case, header_table):
    # FPTNode(attri, count, parent)
    # If child exists, count++
    if case[0] in this_node.child:
        this_node.child[case[0]].count += 1
    # Else, create the child node and link it to this node
    else:
        this_node.child[case[0]] = FPTNode(case[0], 1, this_node)
        # update header table
        if case[0] not in header_table: # first node for this attribute
            header_table[case[0]] = this_node.child[case[0]]
        else: # append the child node to the end of the link
            n = header_table[case[0]]
            while (n.link_next != None):
                n = n.link_next
            n.link_next = this_node.child[case[0]]
    # Recursively create nodes for the rest of the attributes in the data case
    if len(case) > 2: # stop when case[0] is attribute, case[1] is class label
        update_FP_tree(this_node.child[case[0]], case[1::], header_table)
    else: # set the label for the leaf node
        if case[1] in this_node.child[case[0]].labels:
            this_node.child[case[0]].labels[case[1]] += 1
        else:
            this_node.child[case[0]].labels[case[1]] = 1

""" Mine frequent patterns using each frequent attribute as the base """

def projected_db(f_list, header_table, min_sup):
    # reversely go through all the attributes in the F_list
    for e in reversed(f_list):
        attri = (e[0],e[1])
        base_node_h = header_table[attri]
        projected_paths = []
        while base_node_h != None:
            path = []
            base_node = base_node_h
            # look upwards and get all the parent nodes until root
            while base_node.parent != None:
                node_info = [base_node.attri, base_node.count]
                path.append(node_info)
                base_node = base_node.parent  # get the parent node
            path.append(base_node_h.labels)
            projected_paths.append(path)
            # get the next base node in the same link from header table
            base_node_h = base_node_h.link_next
        # Now, all paths for one attribute are retrieved
        # prune infrequent attributes from paths
        freq_attri = OrderedDict()
        for path in projected_paths:
            labels = path.pop(-1) # temporarily store the labels
            for node in path:
                if node[0] not in freq_attri:
                    freq_attri[node[0]] = node[1]
                else:
                    freq_attri[node[0]] += node[1]
            path.append(labels) # append labels back
        # prune infrequent attributes with counts < min_support
        freq_attri = {k: v for k, v in freq_attri.items() if v >= min_sup}
        # construct conditional FP tree for this base
        cond_tree_root = FPTNode('Cond Root', 1, None)
        for path in projected_paths:
            filterd_path = []
            labels = path.pop(-1)  # temporarily store the labels
            for node in reversed(path): # from upper nodes to bottom nodes
                if node[0] in freq_attri: # remove infrequent attri
                    filterd_path.append(node)  # stores attri and count
            path.append(labels)  # append labels back
            if len(filterd_path) == 0:
                continue
            filterd_path.append(labels)
            update_cond_FP_tree(cond_tree_root, filterd_path)

""" Add a path into the conditional FP trees """





"""Main part of the code"""

# test_data = test()
# num_rows = len(test_data)
# min_sup = 0.01 * num_rows
test_data = [
    [1,1,1,1,"A"],
    [1,2,1,2,"B"],
    [2,3,2,3,"A"],
    [1,2,3,3,"C"],
    [1,2,1,3,"C"]
]
min_sup = 2
f_list, value_count = ordered_F_list(test_data, min_sup)
print(f_list)
print(value_count)
FP_tree_root, header_table = create_FP_tree(test_data, f_list)
FP_tree_root.display_tree_list()