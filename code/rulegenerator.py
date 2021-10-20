"""
Rule Generator:
Input: preprocessed data, minimum support and minimum confidence
Output: Class Association Rules (CARs)
"""

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
        # do not add if the ruleitem is already in the set
        is_in_set = False
        for item in self.rule_set:
            if item.label == new_item.label:
                if item.condset == new_item.condset:
                    is_in_set = True
                    break
        if not is_in_set:
            self.rule_set.add(new_item)


class CARs:
    """
    set of Class Association Rules
    """
    def __init__(self):
        self.CARs_rule = set()
        self.pruned_CARs = set()

    def add_CARs_rule(self, rule_item, min_support, min_confidence):
        # basic requirement
        if rule_item.support >= min_support and rule_item.confidence >= min_confidence:
            # do not add if the rule is already in the CARs rule set
            if rule_item in self.CARs_rule:
                return
            # save the ruleitem with the highest confidence when having the same condset
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
        for rule in self.CARs_rule:
            if not should_prune(rule, dataset):
                # add the useful rules into a new set
                self.pruned_CARs.add(rule)

    def join(self, car, min_support, min_confidence):
        """ Add all the ruleitems from another CARs set. """
        for item in car.CARs_rule:
            self.add_CARs_rule(item, min_support, min_confidence)

# get how many data cases do not cover the ruleitem
def get_rule_errors(r, dataset):
    import CBA_CB_M2

    error_num = 0
    for case in dataset:
        if CBA_CB_M2.check_cover(case, r) == False:
            error_num += 1
    return error_num

# return True if the rule should be pruned
def should_prune(rule, dataset):
    min_rule_error = get_rule_errors(rule, dataset)

    if len(rule.condset) > 1:
        for attribute in rule.condset:
            temp_condset = dict(rule.condset) # copy the condset
            temp_condset.pop(attribute)
            temp_rule = ruleitem.RuleItem(temp_condset, rule.label, dataset)
            temp_rule_error = get_rule_errors(temp_rule, dataset)
            if temp_rule_error < min_rule_error:
                return True

    return False


""" Invoked by candidateGen, join two items to generate candidate. """
def join(item1, item2, data_list):
    # 2 ruleItem shall have the same class label
    if item1.label != item2.label:
        return None
    category1 = set(item1.condset)
    category2 = set(item2.condset)
    # 2 ruleItem cannot be the same
    if category1 == category2:
        return None
    # same attribute should have the same value
    shared_attributes = category1 & category2
    for col in shared_attributes:
        if item1.condset[col] != item2.condset[col]:
            return None
    # join 2 ruleItems
    combined_attributes = category1 | category2
    new_condset = {}
    for col in combined_attributes:
        if col in category1:
            new_condset[col] = item1.condset[col]
        else:
            new_condset[col] = item2.condset[col]
    # generate new ruleitem
    new_ruleitem = ruleitem.RuleItem(new_condset, item1.label, data_list)
    return new_ruleitem

# similar to Apriori-gen in algorithm Apriori
def candidateGen(frequent_ruleitems, data_list):
    results = FrequentRuleitemSet()
    for item1 in frequent_ruleitems.rule_set:
        for item2 in frequent_ruleitems.rule_set:
            new_ruleitem = join(item1, item2, data_list)
            if new_ruleitem: # not null
                results.add(new_ruleitem)
                if results.get_num() >= 2000: # 2000 rules limit
                    return results
    return results

# main function to run the rule generator
def rule_generator_main(data_list, min_support, min_confidence):
    frequent_ruleitems = FrequentRuleitemSet()
    new_car = CARs()

    # get large 1-ruleitems and generate CARs_rule
    labels = set([x[-1] for x in data_list]) # set of all lables for each data
    for column in range(0, len(data_list[0])-1):
        distinct_value = set([x[column] for x in data_list]) # set of all values under a column for each data
        for value in distinct_value:
            condset = {column: value}
            for label in labels:
                rule_item = ruleitem.RuleItem(condset, label, data_list) # all possible 1-ruleitems
                if rule_item.support >= min_support:
                    frequent_ruleitems.add(rule_item)
    new_car.copy_freq_rules(frequent_ruleitems, min_support, min_confidence)
    # stores all the CARs 1-ruleitems
    all_CARs = new_car

    current_CARs_num = len(all_CARs.CARs_rule)
    while frequent_ruleitems.get_num() > 0 and current_CARs_num <= 2000: # 2000 rules limit
        candidate = candidateGen(frequent_ruleitems, data_list)
        frequent_ruleitems = FrequentRuleitemSet()
        new_car = CARs()
        # add the candidate ruleitems that meet the basic requirements
        for item in candidate.rule_set:
            if item.support >= min_support:
                frequent_ruleitems.add(item)
        new_car.copy_freq_rules(frequent_ruleitems, min_support, min_confidence)
        all_CARs.join(new_car, min_support, min_confidence)
        current_CARs_num = len(all_CARs.CARs_rule)

    return all_CARs
