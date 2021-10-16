from collections import OrderedDict


""" Data structure for CR-Tree """

class CRTNode:
    def __init__(self, attri, parent):
        self.attri = attri  # attribute tuple: (col, value)
        self.parent = parent  # parent node
        self.child = OrderedDict()  # {attri: child node}
        self.support = None
        self.confidence = None
        self.label = None # class label string
        self.link_next = None  # next node with the same column index in the link


""" Store the rules in CR tree """
""" rule: [a1, b1, ... n1, class label, support, confidence] """

def CRT_add_rule(this_node, rule, header_table):
    # CRTNode(attri, parent)
    # If attribute does not exist, create the child node and link it to this node
    if rule[0] not in this_node.child:
        this_node.child[rule[0]] = CRTNode(rule[0], this_node)
        # update header table
        if rule[0] not in header_table:  # first node for this attribute
            header_table[rule[0]] = this_node.child[rule[0]]
        else:  # append the child node to the end of the link
            n = header_table[rule[0]]
            while (n.link_next != None):
                n = n.link_next
            n.link_next = this_node.child[rule[0]]
    else:
        # check the child node's support and confidence to see if pruning can be done
        if this_node.child[rule[0]].confidence > rule[-1]:
            return
        elif this_node.child[rule[0]].confidence == rule[-1]:
            if this_node.child[rule[0]].support > rule[-2]:
                return
            elif this_node.child[rule[0]].support == rule[-2]:
                if len(rule) > 4:
                    return
    # Recursively create nodes for the rest of the attributes in the rule
    if len(rule) > 4:  # stop when rule is [attribute, class label, support, confidence]
        CRT_add_rule(this_node.child[rule[0]], rule[1::], header_table)
    else:  # set the label, support and confidence for the leaf node
        this_node.child[rule[0]].label = rule[1]
        this_node.child[rule[0]].support = rule[2]
        this_node.child[rule[0]].confidence = rule[3]

        # DFS: search downwards for leaf nodes to prune
        node_to_vist = []
        cur_node = this_node.child[rule[0]] # end node of the new rule
        for key, value in cur_node.child.items():
            node_to_vist.append(value)
        while len(node_to_vist) != 0:
            cur_node = node_to_vist.pop(-1)
            for key, value in cur_node.child.items():
                node_to_vist.append(value)
            if cur_node.support: # encounter an end node of a rule
                # apply pruning method 1
                if cur_node.confidence < rule[-1]:
                    # prune
                    if len(cur_node.child) == 0: # leaf node of the CR Tree
                        while cur_node.parent.support == None and len(cur_node.parent.child) == 1:
                            cur_node = cur_node.parent
                        # keep the last end node or branching node
                        cur_node.parent.child.pop(cur_node.attri)
                    else: # clear the longer rule
                        cur_node.label = None
                        cur_node.suppport = None
                        cur_node.confidence = None
                elif cur_node.confidence == rule[-1]:
                    if cur_node.support <= rule[-2]:
                        # apply pruning method 1
                        if len(cur_node.child) == 0:  # leaf node of the CR Tree
                            while cur_node.parent.support == None and len(cur_node.parent.child) == 1:
                                cur_node = cur_node.parent
                            # keep the last end node or branching node
                            cur_node.parent.child.pop(cur_node.attri)
                        else:  # clear the longer rule
                            cur_node.label = None
                            cur_node.suppport = None
                            cur_node.confidence = None


""" First kind of rule pruning (when a rule is added into the CR Tree) """
""" rule: [attri_1, attri_2, ... attri_n, class label, support, confidence] """
""" attri: (col, value) """
""" data row: [1, 2, ... 1, class label] """
def last_pruning(CR_tree_root, coverage_threshold, data):
    # retrieve all the rules into a list
    rule_list = []
    cur_node = CR_tree_root
    cur_path = []
    node_to_vist = []
    for key, value in cur_node.child.items():
        node_to_vist.append(value)
    while len(node_to_vist) != 0:
        cur_node = node_to_vist.pop(-1)
        cur_path.append(cur_node.attri)
        if cur_node.support: # end node of a rule
            temp_rule = cur_path.copy()
            temp_rule.append(cur_node.attri)
            temp_rule.append(cur_node.label)
            temp_rule.append(cur_node.support)
            temp_rule.append(cur_node.confidence)
            rule_list.append(temp_rule)
        for key, value in cur_node.child.items():
            node_to_vist.append(value)
        if len(cur_node.child) == 0: # leaf node
            cur_path.pop(-1)
            # go upwards until meet a branching node
            while len(cur_node.parent.child) == 1:
                cur_node = cur_node.parent
                cur_path.pop(-1)
    # sort rules in rank descending order
    sorted_rule_list = sorted(rule_list, key=lambda x: (x[-1], x[-2], -len(x)), reverse=True)
    # set each row's cover count to be 0 in the dataset
    temp_data = []
    for row in data:
        temp_data.append(row.copy())
        temp_data[-1].append(0)
    # matching rules and prune
    result_rules = []
    for rule in sorted_rule_list:
        for row in temp_data:
            is_satisfy = True
            for attri in rule[:-3:]:
                if row[attri[0]] != attri[1]:
                    is_satisfy = False
            if is_satisfy:
                row[-1] += 1
                if row[-1] > coverage_threshold:
                    temp_data.remove(row)
        result_rules.append(rule)
        if len(temp_data) == 0:
            break


