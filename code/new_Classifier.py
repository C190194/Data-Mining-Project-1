
""" Assign class label for a data object """

""" Calculate the number of data cases for each class label 
            and the number of rows in the training dataset"""
""" training_data: [ [attri_value_1, attri_value_2, ... , class label], ... ] """

def class_sup_preprocess(training_data):
    class_sup_dic = {}
    for row in training_data:
        if row[-1] not in class_sup_dic:
            class_sup_dic[row[-1]] = 1
        else:
            class_sup_dic[row[-1]] += 1
    return class_sup_dic, len(training_data)

""" Determine class label for the target data object """
""" data_object: [attri_value_1, attri_value_2, attri_value_3, ... ] """
""" t: number of rows in the training dataset """
""" Return the class label string """
def classify(data_object, CR_tree_root, class_sup_dic, t ):
    # Find all the rules matching the data object
    # Assign the rules into dictionary: {class label: [rules] }
    # stored rule: [attri_1, attri_2, ... support, X^2]
    rule_dic = {}
    cur_node = CR_tree_root
    cur_path = []
    node_to_vist = []
    for key, value in cur_node.child.items():
        node_to_vist.append(value)
    while len(node_to_vist) != 0:
        cur_node = node_to_vist.pop(-1)
        # If the attribute is not in the data object
        attri = cur_node.attri
        col = attri[0]
        value = attri[1]
        if data_object[col] != value:
            if len(node_to_vist) == 0: # end the while loop
                break
            # reset path to the parent of the next node to visit
            while node_to_vist[-1].attri not in cur_node.parent.child:
                cur_node = cur_node.parent
                cur_path.pop(-1)
            continue
        # Else, current node matches the data object
        else:
            # append the current node to the path
            cur_path.append(cur_node.attri)
            # If the current node is the end node of a rule
            if cur_node.label:
                label = cur_node.label
                rule = cur_path.copy()
                rule.append(cur_node.support)
                rule.append(cur_node.confidence)
                rule.append(cur_node.x2)
                # add the rule into the rule dictionary
                # rule: [attri_1, attri_2, ... support, X^2]
                if label in rule_dic:
                    rule_dic[label].append(rule)
                else:
                    rule_dic[label] = [rule]
            # add current node's child into nodes to visit
            for key, value in cur_node.child.items():
                node_to_vist.append(value)
            # If current node is a leaf node
            if len(cur_node.child) == 0:
                if len(node_to_vist) == 0: # end the while loop
                    break
                cur_path.pop(-1)
                # reset path to the parent of the next node to visit
                while node_to_vist[-1].attri not in cur_node.parent.child:
                    cur_node = cur_node.parent
                    cur_path.pop(-1)

    # If the data object is not covered by any rule
    # Set the default class as the one with the most count in the training dataset
    if len(rule_dic) == 0:
        return max(class_sup_dic, key=class_sup_dic.get)

    # For each class of rules: calculate weighted X^2
    class_weighted_x2_dic = {}
    for label, rule_list in rule_dic.items():
        weighted_x2 = 0
        for rule in rule_list:
            # rule: [attri_1, attri_2, ... support, confidence, X^2]
            sup_c = class_sup_dic[label]
            # Rule: P->C, calculate sup(P) = sup(R) / confidence
            sup_p = round(rule[-3] / rule[-2])
            # reverse_attributes = rule[-3::-1]
            # last_attri = reverse_attributes[0]
            # base_node_h = FP_header_table[last_attri]
            # # follow the link to go through all the base nodes
            # while base_node_h != None:
            #     attri_to_find = reverse_attributes.copy()
            #     base_node = base_node_h
            #     # look upwards and visit all the parent nodes until root
            #     while base_node.parent != None:
            #         if base_node.attri == attri_to_find[0]:
            #             attri_to_find.pop(0) # found an attribute in the rule
            #         base_node = base_node.parent  # get the parent node
            #     if len(attri_to_find) == 0: # data cases match the rule attributes
            #         sup_p += base_node_h.count
            #     # get the next base node in the same link from header table
            #     base_node_h = base_node_h.link_next
            # calculate e
            e = 1/(sup_c*sup_p) + 1/(sup_p*(t-sup_c)) + 1/(sup_c*(t-sup_p)) + 1/((t-sup_p)*(t-sup_c))
            # calculate max X^2
            max_x2 = (min(sup_c, sup_p) - sup_c*sup_p/t)**2 * t * e
            # update weighted X^2
            x2 = rule[-1]
            weighted_x2 += x2 ** 2 / max_x2
        # record the weighted X^2 for the class
        class_weighted_x2_dic[label] = weighted_x2
    # Select the class with the highest weighted X^2
    result_class = max(class_weighted_x2_dic, key=class_weighted_x2_dic.get)
    return result_class

""" Preprocess X^2 and max X^2 for every rule """
