
from collections import OrderedDict

from preprocessing import test
import new_CR_Tree

""" Data structure for FP-Tree """
class FPTNode:
    def __init__(self, attri, count, parent):
        self.attri = attri  # attribute tuple: (col, value)
        self.count = count  # counts of this value for the attribute
        self.parent = parent  # parent node
        self.child = OrderedDict()  # {attri: child node}
        self.link_next = None  # next node with the same column index in the link
        self.labels = {} # {class label: count}, directly from dataset
        self.accu_labels = {}  # {class label: count}, accumulate labels after tree shrinking




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
    return  F_list


"""This function scans the database for the second time.
The attribute values in each data case are ordered by F_list.
The ordered data case will be added into the FP-Tree."""


def create_FP_tree(test_data, F_list):
    # FPTNode(attri, count, parent)
    root = FPTNode('FP root', 1, None)

    # create empty header table
    header_table = {}

    # add each data case into the FP tree
    for case in test_data:
        ordered_case = []
        for e in F_list:
            if case[e[0]] == e[1]:
                ordered_case.append((e[0], e[1]))
        if len(ordered_case) == 0:
            continue
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
        if len(case) < 2:
            print(case)
        if case[1] in this_node.child[case[0]].labels:
            this_node.child[case[0]].labels[case[1]] += 1
        else:
            this_node.child[case[0]].labels[case[1]] = 1
        # same for accumulated labels after tree shrinking
        if case[1] in this_node.child[case[0]].accu_labels:
            this_node.child[case[0]].accu_labels[case[1]] += 1
        else:
            this_node.child[case[0]].accu_labels[case[1]] = 1

""" Mine frequent patterns using each frequent attribute as the base """

def rule_generator(f_list, FP_header_table, min_sup, min_conf, training_data):
    rule_dic = {}
    # reversely go through all the attributes in the F_list
    # Get the projected database for the base attribute
    for e in reversed(f_list):
        attri = (e[0],e[1])
        base_node_h = FP_header_table[attri]
        projected_paths = []
        while base_node_h != None:
            path = []
            base_node = base_node_h
            # look upwards and get all the parent nodes until root
            while base_node.parent != None:
                node_info = [base_node.attri, base_node_h.count]
                path.append(node_info)
                base_node = base_node.parent  # get the parent node
            # shrink the FP tree by merging accu_labels of the base node and its child nodes
            for attri, FPnode in base_node_h.child.items():
                for label, count in FPnode.accu_labels.items():
                    if label in base_node_h.accu_labels:
                        base_node_h.accu_labels[label] += count
                    else:
                        base_node_h.accu_labels[label] = count
            # add the path into projected database
            path.append(base_node_h.accu_labels)
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

        # rule mining
        filtered_path_list = []
        for path in projected_paths:
            # remove the infrequent attributes from paths
            filterd_path = []
            labels = path.pop(-1)  # temporarily store the labels
            for node in reversed(path): # from upper nodes to bottom nodes
                if node[0] in freq_attri: # remove infrequent attri
                    filterd_path.append(node)  # stores attri and count
            path.append(labels)  # append labels back
            if len(filterd_path) == 0:
                continue
            filterd_path.append(labels)
            filtered_path_list.append(filterd_path)
        # If there's only 1 path, to avoid triviality, make the full path as the rule
        if len(filtered_path_list) == 1:
            rule_attri_list = []
            for node in filtered_path_list[0][:-1:]:
                rule_attri_list.append(node[0])
            rule_attri_tuple = tuple(rule_attri_list)
            # rule_dic: {attributes tuple: {label: count} }
            rule_dic[rule_attri_tuple] = filtered_path_list[0][-1]
        # Else, recursively find frequent patterns for every path
        else:
            for path in filtered_path_list:
                label_dic = path.pop(-1)
                base_tuple = tuple([ path.pop(-1)[0] ])
                attri_list = []
                for node in path:
                    attri_list.append(node[0])
                # use the function defined below
                find_patterns(attri_list, base_tuple, label_dic, rule_dic)
        if len(rule_dic) > 2000:
            break
    # for t, dic in rule_dic.items():
    #     print(t)
    #     print(dic)
    #     print()

    # After all the patterns are added into rule_dic
    # prune the patterns that don't meet min_support or min_confindence
    # then add the rule into CR tree
    rule_count = 0
    CRTroot = new_CR_Tree.CRTNode("CR root", None)
    for rule_attri_tuple, label_dic in rule_dic.items():
        label = max(label_dic, key=label_dic.get)
        # get support
        sup = label_dic[label]
        if sup < min_sup:
            continue
        # get confidence
        total_count = 0
        for l, c in label_dic.items():
            total_count += c
        conf = sup / total_count
        if conf < min_conf:
            continue
        rule = list(rule_attri_tuple)
        rule.append(label)
        rule.append(sup)
        rule.append(conf)
        #print(rule)
        # apply pruning method 2
        if prune_x2(rule, training_data):
            continue
        # add the rule into CR tree
        CR_header_table = {}
        new_CR_Tree.CRT_add_rule(CRTroot, rule, CR_header_table, True)
        rule_count += 1
    #print(rule_count)
    return CRTroot


""" Recursively find frequent patterns for every path """

def find_patterns(attri_list, base_tuple, label_dic, rule_dic):
    if len(rule_dic) > 2000:
        return
    for i in range(len(attri_list)):
        rule_attri_list = list(base_tuple)
        rule_attri_list.append(attri_list[i])
        rule_attri_tuple = tuple(rule_attri_list)
        if rule_attri_tuple in rule_dic:
            for label, count in label_dic.items():
                if label in rule_dic[rule_attri_tuple]:
                    rule_dic[rule_attri_tuple][label] += count
                else:
                    rule_dic[rule_attri_tuple][label] = count
        else:
            rule_dic[rule_attri_tuple] = label_dic

        if i != 0:
            new_attri_list = attri_list[:i:]
            find_patterns(new_attri_list, rule_attri_tuple, label_dic, rule_dic)




""" Pruning method 2: """
""" Perform X^2 testing when a rule is found """
""" rule: [attri_1, attri_2, ... class label, support, confidence]"""
""" return True if the rule should be pruned
    return False if the rule should not be pruned """

def prune_x2(rule, data):
    # X^2 thresholds (Probability = 0.05) for degree of freedom 1~30
    # Reference: https://www.bmj.com/sites/default/files/attachments/resources/2011/08/appendix-table-c.pdf
    x2_005_threshold = [3.841, 5.991, 7.815, 9.488, 11.070,
                        12.592, 14.067, 15.507, 16.919, 18.307,
                        19.675, 21.026, 22.362, 23.685, 24.996,
                        26.296, 27.587, 28.869, 30.144, 31.410,
                        32.671, 33.924, 35.172, 36.415, 37.652,
                        38.885, 40.113, 41.337, 42.557, 43.773 ]
    # initialize X^2 table for this rule:
    """ { class label : { "match" : #,
                          "miss" : #},
        ...
        } """
    x2_table = {}
    x2 = 0
    total_match_num = 0
    total_miss_num = 0
    total_row_num = len(data)
    # update the X^2 table for every row of data
    for row in data:
        is_match = True
        for attri in rule[:-3:]:
            col = attri[0]
            value = attri[1]
            if row[col] != value:
                is_match = False
                break
        if is_match:
            total_match_num += 1
            if row[-1] not in x2_table:
                x2_table[row[-1]] = { "match" : 1,
                                       "miss" : 0}
            else:
                x2_table[row[-1]]["match"] += 1
        else: # data row does not match the rule
            total_miss_num += 1
            if row[-1] not in x2_table:
                x2_table[row[-1]] = { "match" : 0,
                                       "miss" : 1}
            else:
                x2_table[row[-1]]["miss"] += 1
    #print(x2_table)
    # calculate X^2 value
    for label, dic in x2_table.items():
        # for "match" value
        expected_value = (dic["match"] + dic["miss"]) * total_match_num / total_row_num
        x2 += (dic["match"] - expected_value) ** 2
        # for "miss" value
        expected_value = (dic["match"] + dic["miss"]) * total_miss_num / total_row_num
        x2 += (dic["miss"] - expected_value) ** 2
    # append x2 value in the rule item
    rule.append(x2)
    # check if X^2 value >= threshold
    degree_freedom = len(x2_table) - 1
    #print(degree_freedom)
    if x2 >= x2_005_threshold[degree_freedom - 1]:
        return False
    else: # should be pruned
        return True







# """Main part of the code"""
#
# # test_data = test()
# # num_rows = len(test_data)
# # min_sup = 0.01 * num_rows
# test_data = [
#     [1,1,1,1,"A"],
#     [1,2,1,2,"B"],
#     [2,3,2,3,"A"],
#     [1,2,3,3,"C"],
#     [1,2,1,3,"C"]
# ]
# min_sup = 2
# f_list, value_count = ordered_F_list(test_data, min_sup)
# print(f_list)
# print(value_count)
# FP_tree_root, header_table = create_FP_tree(test_data, f_list)
# FP_tree_root.display_tree_list()
