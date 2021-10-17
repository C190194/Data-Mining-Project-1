"""
Rule Generator:
Input: preprocessed data, minimum support and minimum confidence
Output: Class Association Rules (CARs)
"""
import sys
import ruleitem
from readfile import read_files
from preprocessing import preprocessing_main

class FrequentRuleitemSet:
    """
    A set of frequent k-ruleitems, just using set.
    """
    def __init__(self):
        self.rule_set = set()

    
    def get_num(self):
        """ Get size of set. """
        return len(self.rule_set)


    def add(self, new_item):
        """ Add a new ruleitem into set. """
        is_in_set = False
        for item in self.rule_set:
            if item.label == new_item.label:
                if item.condset == new_item.condset:
                    is_in_set = True
                    break
        if not is_in_set:
            self.rule_set.add(new_item)

    
    def print(self):
        """ Print out all frequent ruleitems. """
        for item in self.rule_set:
            item.print()


class CARs:
    """
    Class Association Rules (CARs). If some ruleitems has the same condset, the ruleitem with the highest confidence is
    chosen as the Possible Rule (PR). If there're more than one ruleitem with the same highest confidence, we randomly
    select one ruleitem.
    """
    def __init__(self):
        self.CARs_rule = set()
        self.pruned_CARs = set()

    def print_CARs(self):
        """ Print out all CARs_rule. """
        for item in self.CARs_rule:
            item.print_rule()


    def print_pruned_CARs(self):
        """ Print out all pruned CARs_rule. """
        for item in self.pruned_CARs:
            item.print_rule()


    def add_CARs_rule(self, rule_item, min_support, min_confidence):
        """ Add a new rule (frequent & accurate).
        Save the ruleitem with the highest confidence when having the same condset. """
        if rule_item.support >= min_support and rule_item.confidence >= min_confidence:
            if rule_item in self.CARs_rule:
                return None
            for item in self.CARs_rule:
                if item.condset == rule_item.condset and item.confidence < rule_item.confidence:
                    self.CARs_rule.remove(item)
                    self.CARs_rule.add(rule_item)
                    return
                elif item.condset == rule_item.condset and item.confidence >= rule_item.confidence:
                    return
            self.CARs_rule.add(rule_item)


    def copy_freq_rules(self, frequent_ruleitems, min_support, min_confidence):
        """ Copy the frequent k-ruleitems set to CARs rule set. """
        for item in frequent_ruleitems.rule_set:
            self.add_CARs_rule(item, min_support, min_confidence)
            

    def prune_rules(self, dataset):
        """ prun rules function that recursively prune rules."""
        for rule in self.CARs_rule:
            pruned_rule = prune(rule, dataset)

            is_in_set = False
            for rule in self.pruned_CARs:
                if rule.label == pruned_rule.label:
                    if rule.condset == pruned_rule.condset:
                        is_in_set = True
                        break

            if not is_in_set:
                self.pruned_CARs.add(pruned_rule)

    def join(self, car, min_support, min_confidence):
        """ Add all the ruleitems from another CARs set. """
        for item in car.CARs_rule:
            self.add_CARs_rule(item, min_support, min_confidence)


def prune(rule, dataset):
    """ Prune rule. """
    import sys
    min_rule_error = sys.maxsize
    pruned_rule = rule

    # prune rule recursively
    def find_prune_rule(this_rule):
        nonlocal min_rule_error
        nonlocal pruned_rule

        # calculate how many errors the rule r make in the dataset
        def get_rule_errors(r):
            import CBA_CB_M1

            error_num = 0
            for case in dataset:
                if CBA_CB_M1.check_cover(case, r) == False:
                    error_num += 1
            return error_num

        rule_errors = get_rule_errors(this_rule)
        if rule_errors < min_rule_error:
            min_rule_error = rule_errors
            pruned_rule = this_rule
        this_rule_condset = list(this_rule.condset)
        if len(this_rule_condset) >= 2:
            for attribute in this_rule_condset:
                temp_condset = dict(this_rule.condset)
                temp_condset.pop(attribute)
                temp_rule = ruleitem.RuleItem(temp_condset, this_rule.label, dataset)
                temp_rule_error = get_rule_errors(temp_rule)
                if temp_rule_error <= min_rule_error:
                    min_rule_error = temp_rule_error
                    pruned_rule = temp_rule
                    if len(temp_condset) >= 2:
                        find_prune_rule(temp_rule)

    find_prune_rule(rule)
    return pruned_rule



def join(item1, item2, data_list):
    """ Invoked by candidateGen, join two items to generate candidate. """
    if item1.label != item2.label:
        return None
    category1 = set(item1.condset)
    category2 = set(item2.condset)
    if category1 == category2:
        return None
    intersect = category1 & category2
    for item in intersect:
        if item1.condset[item] != item2.condset[item]:
            return None
    category = category1 | category2
    new_condset = dict()
    for item in category:
        if item in category1:
            new_condset[item] = item1.condset[item]
        else:
            new_condset[item] = item2.condset[item]
    new_ruleitem = ruleitem.RuleItem(new_condset, item1.label, data_list)
    return new_ruleitem


def candidateGen(frequent_ruleitems, data_list):
    """ This function is similar to Apriori-gen in Apriori algorithm. """
    returned_frequent_ruleitems = FrequentRuleitemSet()
    for item1 in frequent_ruleitems.rule_set:
        for item2 in frequent_ruleitems.rule_set:
            new_ruleitem = join(item1, item2, data_list)
            if new_ruleitem:
                returned_frequent_ruleitems.add(new_ruleitem)
                 # do not allowed to store more than 1000 ruleitems
                if returned_frequent_ruleitems.get_num() >= 1000:     
                    return returned_frequent_ruleitems
    return returned_frequent_ruleitems


def rule_generator_main(data_list, min_support, min_confidence):
    """ Main function here."""
    frequent_ruleitems = FrequentRuleitemSet()
    new_car = CARs()

    # get large 1-ruleitems and generate CARs_rule
    labels = set([x[-1] for x in data_list])
    for column in range(0, len(data_list[0])-1):
        distinct_value = set([x[column] for x in data_list])
        for value in distinct_value:
            condset = {column: value}
            for label in labels:
                rule_item = ruleitem.RuleItem(condset, label, data_list)
                if rule_item.support >= min_support:
                    frequent_ruleitems.add(rule_item)
    new_car.copy_freq_rules(frequent_ruleitems, min_support, min_confidence)
    all_CARs = new_car

    previous_CARs_num = 0
    current_CARs_num = len(all_CARs.CARs_rule)
    while frequent_ruleitems.get_num() > 0 and current_CARs_num <= 2000 and \
                    (current_CARs_num - previous_CARs_num) >= 10:
        candidate = candidateGen(frequent_ruleitems, data_list)
        frequent_ruleitems = FrequentRuleitemSet()
        new_car = CARs()
        for item in candidate.rule_set:
            if item.support >= min_support:
                frequent_ruleitems.add(item)
        new_car.copy_freq_rules(frequent_ruleitems, min_support, min_confidence)
        all_CARs.join(new_car, min_support, min_confidence)
        previous_CARs_num = current_CARs_num
        current_CARs_num = len(all_CARs.CARs_rule)

    return all_CARs


# just for test
if __name__ == "__main__":
    test_data_path = 'C:/Users/XPS/Desktop/Uni drives me crazy/Y3S1/CZ4032 Data Analytics and Mining/Data-Mining-Project-1/dataset/zoo.data'
    test_names_path = 'C:/Users/XPS/Desktop/Uni drives me crazy/Y3S1/CZ4032 Data Analytics and Mining/Data-Mining-Project-1/dataset/zoo.names'
    data_list, attributes, attribute_types = read_files(test_data_path, test_names_path)
    data_list = preprocessing_main(data_list, attributes, attribute_types)
    min_support = 0.01
    min_confidence = 0.5
    CARs = rule_generator_main(data_list, min_support, min_confidence)

    print("CARs:")
    CARs.print_CARs()

    print("prCARs:")
    CARs.prune_rules(data_list)
    CARs.print_pruned_CARs()
