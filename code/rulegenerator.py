"""
Rule Generator:
Input: preprocessed data, minimum support and minimum confidence
Output: Class Association Rules (CARs)
"""
import sys
import ruleitem

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
        """ Prune rules from CARs. """
        for rule in self.CARs_rule:
            pruned_rule = pruning(rule, dataset)

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


def pruning(rule, dataset):
    """ Prune rule. """
    min_rule_error = sys.maxsize
    pruned_rule = rule
    
    def find_prune_rule(this_rule):
        """ Pruning the rule recursively. """
        nonlocal min_rule_error
        nonlocal pruned_rule

        # calculate how many errors the rule ruleitem make in the dataset
        def get_error_num(ruleitem):
            import CBA_CB_M1

            error_num = 0
            for data_line in dataset:
                if CBA_CB_M1.check_cover(data_line, ruleitem) == False:
                    error_num += 1
            return error_num

        rule_error = get_error_num(this_rule)
        if rule_error < min_rule_error:
            min_rule_error = rule_error
            pruned_rule = this_rule
        this_rule_cond_set = list(this_rule.condset)
        if len(this_rule_cond_set) >= 2:
            for attribute in this_rule_cond_set:
                temp_cond_set = dict(this_rule.condset)
                temp_cond_set.pop(attribute)
                temp_rule = ruleitem.RuleItem(temp_cond_set, this_rule.label, dataset)
                temp_rule_error = get_error_num(temp_rule)
                if temp_rule_error <= min_rule_error:
                    min_rule_error = temp_rule_error
                    pruned_rule = temp_rule
                    if len(temp_cond_set) >= 2:
                        find_prune_rule(temp_rule)

    find_prune_rule(rule)
    return pruned_rule


# invoked by candidateGen, join two items to generate candidate
def join(item1, item2, dataset):
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
    new_cond_set = dict()
    for item in category:
        if item in category1:
            new_cond_set[item] = item1.condset[item]
        else:
            new_cond_set[item] = item2.condset[item]
    new_ruleitem = ruleitem.RuleItem(new_cond_set, item1.label, dataset)
    return new_ruleitem


# similar to Apriori-gen in algorithm Apriori
def candidateGen(frequent_ruleitems, dataset):
    returned_frequent_ruleitems = FrequentRuleitemSet()
    for item1 in frequent_ruleitems.rule_set:
        for item2 in frequent_ruleitems.rule_set:
            new_ruleitem = join(item1, item2, dataset)
            if new_ruleitem:
                returned_frequent_ruleitems.add(new_ruleitem)
                if returned_frequent_ruleitems.get_num() >= 1000:      # not allow to store more than 1000 ruleitems
                    return returned_frequent_ruleitems
    return returned_frequent_ruleitems


# main method, implementation of CBA-RG algorithm
def rule_generator_main(dataset, min_support, min_confidence):
    frequent_ruleitems = FrequentRuleitemSet()
    new_car = CARs()

    # get large 1-ruleitems and generate CARs_rule
    labels = set([x[-1] for x in dataset])
    for column in range(0, len(dataset[0])-1):
        distinct_value = set([x[column] for x in dataset])
        for value in distinct_value:
            condset = {column: value}
            for label in labels:
                rule_item = ruleitem.RuleItem(condset, label, dataset)
                if rule_item.support >= min_support:
                    frequent_ruleitems.add(rule_item)
    new_car.copy_freq_rules(frequent_ruleitems, min_support, min_confidence)
    all_CARs = new_car

    previous_CARs_num = 0
    current_CARs_num = len(all_CARs.CARs_rule)
    while frequent_ruleitems.get_num() > 0 and current_CARs_num <= 2000 and \
                    (current_CARs_num - previous_CARs_num) >= 10:
        candidate = candidateGen(frequent_ruleitems, dataset)
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
    dataset = [[1, 1, 1], [1, 1, 1], [1, 2, 1], [2, 2, 1], [2, 2, 1],
               [2, 2, 0], [2, 3, 0], [2, 3, 0], [1, 1, 0], [3, 2, 0]]
    min_support = 0.15
    min_confidence = 0.6
    CARs = rule_generator_main(dataset, min_support, min_confidence)

    print("CARs:")
    CARs.print_CARs()

    print("prCARs:")
    CARs.prune_rules(dataset)
    CARs.print_pruned_CARs()
