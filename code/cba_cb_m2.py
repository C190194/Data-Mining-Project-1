"""
    Implementation of CBA-CB_M2 Classifier. The main function contains three stages. 
    For stage 1, we scan the whole database to find the cRule and wRule, get the set Q, U and A at the same
    time. In stage 2, for each data case d that we could not decide which rule should cover it in stage 1, we go through d
    again to find all rules that classify it wrongly and have a higher precedence than the corresponding cRule of d.
    Finally, in stage 3, we choose the final set of rules to form our final classifer.
Input: a set of CARs generated from rule_generator (see cab_rg.py) and a data_list got from preprocessing.py

Output: classifier_M2
"""
import sys
import ruleitem
import CBA_CB_M1
from functools import cmp_to_key


class Classifier_M2:
    """
    Build the class for classifier_M2. 
    The definition of classifier_M2 formed in CBA-CB: M2. 
    It contains a list of generated rules order by precedence and a default class label. 
    The other member are private and useless for outer code.
    """
    def __init__(self):
        self.rule_list = list()
        self.default_label = None
        self.num_errors_list = list()
        self.default_label_list = list()

    def rule_insertion(self, rule, default_label, num_errors):
        """ Insert a new rule into the classifier_M2. """
        # append the parameters to the respective list
        self.rule_list.append(rule)
        self.default_label_list.append(default_label)
        self.num_errors_list.append(num_errors)

    # discard those rules that introduce more errors. See line 18-20, CBA-CB: M2 (Stage 3).
    def rule_cleaning(self):
        """ Find the rule with the minimum number of total erros.
        Drop all the remaining rules after that rule. """
        # find the minimum number of errors in the list
        min_errors = min(self.num_errors_list)
        # fine the rule's index position
        position = self.num_errors_list.index(min_errors)
        # discard all the rules after
        self.rule_list = self.rule_list[:(index + 1)]
        self.num_errors_list = None
        # assign the default label 
        # to be the label at the same position index as the rule in the default_label_list
        self.default_label = self.default_label_list[position]
        self.default_label_list = None
        

    def print(self):
        """ A print function that print out all the selected rules 
        and default class label in the classifier_M2. """
        for rule in self.rule_list:
            rule.print_rule()
        print("Default class label:", self.default_label)


class Rule(ruleitem.RuleItem):
    """
    Build a Rule class that inherite RuleItem class.
    Adding num_label_covered to record the number of times cRule covered each class label
    and replace field.
    """
    def __init__(self, condset, label, data_list):
        # Inerite the class attributes from RuleItem
        ruleitem.RuleItem.__init__(self, condset, label, data_list)
        # Add other class attributes
        self._init_num_label_covered(data_list)
        self.replace = set()

    def _init_num_label_covered(self, data_list):
        """ Initialize the num_label_covered. 
        This is the same as classCasesCovered field in the paper. """
        # find the label column, which is at the last column
        label_column = [x[-1] for x in data_list]
        # find all distinct labels
        labels = set(label_column)
        # build a dictionary for num_label_covered
        self.num_label_covered = dict((label, 0) for label in labels)


def ruleitem_to_rule(ruleitem, data_list):
    """ Convert the ruleitem in RuleItem class to rule in Rule class. """
    rule = Rule(ruleitem.condset, ruleitem.label, data_list)
    return rule


def find_cRule_index(CARs_list, data):
    """ Stage 1: Find the highest precedence rule cRule (in paper) that correctly classifies data case d
    from the set of rule having the same class label as d. 
    This function is the same as 'maxCoverRule' in paper. """
    CARs_length = len(CARs_list)
    for index in range(CARs_length):
        # if they belongs to the same class label
        if CARs_list[index].label == data[-1]:
            # check wether the rule in the cars_list cover the single data line
            if CBA_CB_M1.check_cover(data, CARs_list[index]):
                # if ture, return the index
                return index
    return None


# finds the highest precedence rule that covers the data case d from the set of rules having the different class as d.
def find_wRule_index(CARs_list, data):
    """ Stage 1: Find the highest precedence rule wRule (in paper) that wrongly classifies data case d
    from the set of rule having the different class label as d. """
    CARs_length = len(CARs_list)
    for index in range(CARs_length):
        # if the have different class label
        if CARs_list[index].label != data[-1]:
            # create a temporary data case that without the class label
            temporary_data = data[:-1]
            # append the class label in the rule to the temporary data case
            temporary_data.append(CARs_list[index].label)
            # if the rule in CARs_list can cover the temporary data line
            if CBA_CB_M1.check_cover(temporary_data, CARs_list[index]):
                # return the index
                return index
    return None


def compare_rules(r1, r2):
    """ Comapre two rules based on precedence.
    return 1: if r1 > r2
    return 0: if r1 = r2
    return -1: if r2 > r1 """
    if r1 is not None and r2 is None:
        return 1
    elif r1 is None and r2 is None:
        return 0
    elif r1 is None and r2 is not None:
        return -1
    # 1. confidence of r2 > r1, r2 have higher precedence
    if r2.confidence > r1.confidence:     
        return -1
    # 2. confidences are the same
    elif r1.confidence == r2.confidence:
        # but support of r2 > r1, r2 have higher precedence
        if rule2.support > rule1.support:       
            return -1
        # 3. confidence and support are the same, 
        elif r1.support == r2.support:
            # but r1 generated earlier than r2, r1 have higher precedence
            if len(r1.condset) < len(r2.condset):    
                return 1 
            # if all conditions are the same, return 0                           
            elif len(r1.condset) == len(r2.condset):
                return 0
            else:
                return -1
        else:
            return 1
    else:
        return 1


def find_wSet(U, data, cRule, CARs_list):
    """ Stage2: Find all the rules in U: the set of all cRules (as stated in the paper)
    that wrongly classify the data line 
    and have higher precedence than that of its cRule. """
    wSet = set()
    for index in U:
        # if the rule have higher precedences than cRule
        if compare_rules(CARs_list[index], cRule) > 0:
            # and it does not cover the data line
            if CBA_CB_M1.check_cover(data, CARs_list[index]) == False:
                # add the index
                wSet.add(index)
    return wSet


def find_label_count(data_list):
    """ Count the number of data cases in each class label. """
    # Initialize an empty dictionary
    label_count = dict()
    
    # in the case if there are no data in the data_list
    if len(data_list) <= 0:
        label_count = None

    label_column = [x[-1] for x in data_list]
    labels = set(label_column)
    for label in labels:
        # count the number of each labels and add to the dictionary
        label_count[label] = label_column.count(label)
    return label_count


def sort_CARs(Q, CARs_list):
    """ Sort the list of generated class association rules in descending order.
    The order is based on the relation ">" in precendence.
    Return the sorted rule list.
    Q: the set of cRules that have a higher precedence than their corresponding wRules. """
    def compare_rules(i, j):
        # 1. the confidence of rj > ri
        if CARs_list[j].confidence > CARs_list[i].confidence:
            return 1
        # 2. their confidences are the same
        elif CARs_list[i].confidence == CARs_list[j].confidence:
            # but support of rj > ri
            if CARs_list[j].support > CARs_list[i].support:
                return 1
            # if both confidence and support are the same
            elif CARs_list[i].support == CARs_list[j].support:
                # but ri is generated earlier than rj
                if len(CARs_list[i].condset) < len(CARs_list[j].condset):
                    return -1
                # if all conditions are the same
                elif len(CARs_list[i].condset) == len(CARs_list[j].condset):
                    return 0
                else:
                    return 1
            else:
                return -1
        else:
            return -1

    rule_list = list(Q)
    # sort the rule_list based on precedence
    rule_list.sort(key=cmp_to_key(compare_rules))
    return set(rule_list)


def count_rule_errors(rule, data_list):
    """ Count the number of errors that a rule wrongly classify a data line. """
    num_errors = 0
    # iterate through each single line of data_list
    for line in data_list:
        if line:
            # check if it correcly classify the data
            if CBA_CB_M1.check_cover(line, rule) == False:
                # if false, number of errors + 1
                num_errors += 1
    return num_errors



def default_label_selection(label_count):
    """ Find the default class label, 
    which is the label with the highest frequency in the reamining data_list. """
    if label_count is None:
        return None
    max_count = 0
    # Initialization
    default_label = None
    # a for loop to find the label with maximum frequency
    for label in label_count:
        if label_count[label] > max_count:
            # update max_count
            max_count = label_count[label]
            default_label = label
    return default_label

def count_default_label_errors(default_label, label_count):
    """ Count the total number of errors that the selected default label will make
    in the remainig data_list. """
    if label_count is None:
        return sys.maxsize
    # Initialization
    num_errors = 0
    for label in label_count:
        # if the label is different from the default label
        if label != default_label:
            # number of errors + label_count of that label
            num_errors += label_count[label]
    return num_errors


def build_classifier_M2(CARs, data_list):
    """ This is the main function of the M2 classifier that combine everything
    to build the compelete classifier. """
    classifier_M2 = Classifier_M2()

    CARs_list = CBA_CB_M1.sort_CARs(cars)
    CARs_length = len(CARs_list)
    for index in range(CARs_length):
        CARs_list[index] = ruleitem_to_rulerule(CARs_list[index], data_list)

    # Stage 1 in the paper
    # Q is the set of cRules that have a higher precedence than their corresponding wRules
    Q = set()
    # U is the set of all cRules
    U = set()
    # A is the collection of <dID, y, cRule, wRule>
    A = set()
    # mark the cRule to indicate it classifies a data case correctly
    mark = set()
    data_size = len(data_list)
    for data_index in range(data_size):
        cRule_index = find_cRule_index(CARs_list, data_list[data_index])
        wRule_index = find_wRule_index(CARs_list, data_list[data_index])
        if cRule_index is not None:
            # add to U
            U.add(cRule_index)
        if cRule_index:
            # the count of label covered by the cRule + 1
            CARs_list[cRule_index].num_label_covered[data_list[data_index][-1]] += 1
        # if there exist both cRule and wRule,  compare their precedence
        if cRule_index and wRule_index:
            # if cRule have a higher precedence then wRule, cRule > wRule
            if compare_rules(CARs_list[cRule_index], CARs_list[wRule_index]) == 1:
                # add the cRule_index to Q set according to the paper
                Q.add(cRule_index)
                # mark the cRule
                mark.add(cRule_index)
            # if wRule > cRule
            else:
                # complex case, cannot decide which rule will eventually cover the data case
                # add the collection of values into A set as stated in the paper <dID, y, cRule, wRule>
                A.add((data_index, data_list[data_index][-1], cRule_index, wRule_index))
        # add the collection <dID, y, cRule, wRule>
        elif cRule_index is None and wRule_index is not None:
            A.add((data_index, data_list[data_index][-1], cRule_index, wRule_index))

    # Stage 2 in the paper
    # interate through each collection in A set
    for collection in A:
        # if the wRule is marked, which means it is the cRule of at least once
        # This satisfy the 2 conditions.
        if CARs_list[collection[3]] in mark:
            # check if cRule is empty, if not emppty
            if collection[2] is not None:
                # update the number of label covered by the rule
                # num_label_covered by cRule - 1
                CARs_list[collection[2]].num_label_covered[collection[1]] -= 1
            # num_label_covered by wRule + 1
            CARs_list[collection[3]].num_label_covered[collection[1]] += 1
        # if wRule is not marked
        else:
            if collection[2] is not None:
                # find all the cRules in U that wrongly classify the data case 
                # and have a higher precedences than that of its cRule
                # this is also called the allCoverRules() in the paper
                wSet = find_wSet(U, data_list[collection[0]], CARs_list[collection[2]], CARs_list)
            else:
                wSet = find_wSet(U, data_list[collection[0]], None, CARs_list)
            # iterate each rule w in the wSet
            for rule_w in wSet:
                # the rule_w may replace cRule to cover the data case as they have higher precedences
                CARs_list[rule_w].replace.add((collection[2], collection[0], collection[1]))
                # the numbrt of label covered count by rule_w + 1 as the rule_w may cover the data case
                CARs_list[rule_w].num_label_covered[collection[1]] += 1
            # Q union wSet as Q should contains all the rules to be used to build the classifier_M2
            Q |= wSet

    # Stage 3 in the paper
    # Choose a set of potential rules to form the classifier_M2
    num_rule_errors = 0
    data_size = len(data_list)
    # Sort the Q according to relation ">"
    Q = sort_CARs(Q, CARs_list)
    # Initialize all cover to Flase
    data_line_covered = list([False] * data_size)
    for rule_index in Q:
        # If the rule no longer classifies any data cass, we discard it.
        # Otherwise the rule will be used for the classifier_M2.
        if CARs_list[rule_index].num_label_covered[CARs_list[rule_index].label] != 0:
            # the rule will try to replace all the rules in the CARs_list[rule_index].replace
            # as the rule precedess them
            for entry in CARs_list[rule_index].replace:
                # if the data case line has been covered by a previous rule
                # the current rule will replace previous rule to cover the case
                if data_line_covered[entry[1]]:
                    # update the num_label_covered by the current rule
                    CARs_list[rule_index].num_label_covered[entry[2]] -= 1
                else:
                    # the current rule will replace the previous rule to cover the data case line
                    if entry[0] is not None:
                        # update the num_label_covered by the previous rule
                        CARs_list[entry[0]].num_label_covered[entry[2]] -= 1
            # iterae through each data case line
            for data_index in range(data_size):
                data_line = data_list[data_index]
                if data_line:
                    is_covered = CBA_CB_M1.check_cover(data_line, CARs_list[rule_index])
                    # if True
                    if is_covered:
                        data_list[data_index] = []
                        # update the covered status to True
                        data_line_covered[data_index] = True
            # for each rule, update the number of rule errors
            num_rule_errors += count_rule_errors(CARs_list[rule_index], data_list)
            # update the label count
            label_count = find_label_count(data_list)
            default_label = default_label_selection(label_count)
            # count the total number of errors that the selected default label will make
            # in the remainig data_list
            default_label_errors = count_default_label_errors(default_label, label_count)
            # calculate total errors that the seleced rules and the default label will make
            total_errors = num_rule_errors + default_label_errors
            # add them to the classifier_M2
            classifier_M2.add(CARs_list[rule_index], default_class, total_errors)
    # discard all the rules introduce more errors, and return the final classifier
    classifier_M2.rule_cleaning()

    return classifier_M2


# just for test
if __name__ == "__main__":
    import cba_rg

    data_list = [[1, 1, 1], [1, 1, 1], [1, 2, 1], [2, 2, 1], [2, 2, 1],
               [2, 2, 0], [2, 3, 0], [2, 3, 0], [1, 1, 0], [3, 2, 0]]
    minsup = 0.15
    minconf = 0.6
    cars = cba_rg.rule_generator(data_list, minsup, minconf)
    classifier_M2 = build_classifier_M2(cars, data_list)
    classifier_M2.print()

    print()
    data_list = [[1, 1, 1], [1, 1, 1], [1, 2, 1], [2, 2, 1], [2, 2, 1],
               [2, 2, 0], [2, 3, 0], [2, 3, 0], [1, 1, 0], [3, 2, 0]]
    cars.prune_rules(data_list)
    cars.rules = cars.pruned_rules
    classifier_M2 = build_classifier_M2(cars, data_list)
    classifier_M2.print()
