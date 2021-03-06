from collections import OrderedDict


""" Data structure for CR-Tree """

class CRTNode:
    def __init__(self, attri, parent):
        self.attri = attri  # attribute tuple: (col, value)
        self.parent = parent  # parent node
        self.child = {}  # {attri: child node}
        self.support = None
        self.confidence = None
        self.x2 = None # X^2 value
        self.label = None # class label string
        self.link_next = None  # next node with the same column index in the link


""" Store the rules in CR tree """
""" rule: [a1, b1, ... n1, class label, support, confidence, X^2] """

def CRT_add_rule(this_node, rule, header_table, apply_prune):
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
        if apply_prune:
            # If the added node is an end node of another rule
            if this_node.child[rule[0]].confidence:
                # check the child node's support and confidence to see if pruning can be done
                if this_node.child[rule[0]].confidence > rule[-2]:
                    return
                elif this_node.child[rule[0]].confidence == rule[-2]:
                    if this_node.child[rule[0]].support > rule[-3]:
                        return
                    elif this_node.child[rule[0]].support == rule[-3]:
                        if len(rule) > 5:
                            return
    # Recursively create nodes for the rest of the attributes in the rule
    if len(rule) > 5:  # stop when rule is [attribute, class label, support, confidence, X^2]
        CRT_add_rule(this_node.child[rule[0]], rule[1::], header_table, apply_prune)
    else:  # set the label, support and confidence for the leaf node
        this_node.child[rule[0]].label = rule[1]
        this_node.child[rule[0]].support = rule[2]
        this_node.child[rule[0]].confidence = rule[3]
        this_node.child[rule[0]].x2 = rule[4]

        if apply_prune:
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
                    if cur_node.confidence < rule[-2]:
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
                            cur_node.x2 = None
                    # elif cur_node.confidence == rule[-2]:
                    #     if cur_node.support <= rule[-3]:
                    #         # prune
                    #         if len(cur_node.child) == 0:  # leaf node of the CR Tree
                    #             while cur_node.parent.support == None and len(cur_node.parent.child) == 1:
                    #                 cur_node = cur_node.parent
                    #             # keep the last end node or branching node
                    #             cur_node.parent.child.pop(cur_node.attri)
                    #         else:  # clear the longer rule
                    #             cur_node.label = None
                    #             cur_node.suppport = None
                    #             cur_node.confidence = None
                    #             cur_node.x2 = None


""" First kind of rule pruning (when a rule is added into the CR Tree) """
""" rule: [attri_1, attri_2, ... attri_n, class label, support, confidence, X^2] """
""" attri: (col, value) """
""" data row: [1, 2, ... 1, class label] """
def last_pruning(CR_tree_root, coverage_threshold, data):
    newCRTroot = CRTNode("CR root", None)
    new_CR_header_table = {}
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
            temp_rule.append(cur_node.label)
            temp_rule.append(cur_node.support)
            temp_rule.append(cur_node.confidence)
            temp_rule.append(cur_node.x2)
            rule_list.append(temp_rule)
        for key, value in cur_node.child.items():
            node_to_vist.append(value)
        if len(cur_node.child) == 0: # leaf node
            if len(node_to_vist) == 0: # end the while loop
                break
            cur_path.pop(-1)
            # reset path to the parent of the next node to visit
            while node_to_vist[-1].attri not in cur_node.parent.child:
                cur_node = cur_node.parent
                cur_path.pop(-1)
    # sort rules in rank descending order
    sorted_rule_list = sorted(rule_list, key=lambda x: (x[-2], x[-3], -len(x)), reverse=True)
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
            for attri in rule[:-4:]:
                if row[attri[0]] != attri[1]:
                    is_satisfy = False
                    break
            if is_satisfy:
                row[-1] += 1
                if row[-1] > coverage_threshold:
                    temp_data.remove(row)
        result_rules.append(rule)
        CRT_add_rule(newCRTroot, rule, new_CR_header_table, False)
        if len(temp_data) == 0:
            break
    #print("Final rules:")
    #print(result_rules)
    return newCRTroot, new_CR_header_table, len(result_rules)


