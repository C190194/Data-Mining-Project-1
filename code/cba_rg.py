"""
Rule Generator:
Input: preprocessed data, minimum support and minimum confidence
Output: Class Association Rules (CAR)
"""
import ruleitem


class FrequentRISet:
    """
    A set of frequent k-ruleitems
    """
    def __init__(self):
        self.rule_set = set()

    # get number of frequent k-ruleitems in the set
    def get_num(self):
        return len(self.rule_set)

    # add another ruleitem
    def add(self, new_item):
        # do not add if the ruleitem is already in the set
        is_in_set = False
        for i in self.rule_set:
            if i.label == new_item.label: 
                if i.condset == new_item.condset: 
                    is_in_set = True
                    break
        # add the new ruleitem
        if not is_in_set:
            self.rule_set.add(new_item)

    # *** not used
    # add the car_rule_set from another FrequentRISet
    def append(self, new_set):
        for item in new_set.frequent_ruleitems:
            self.add(item)

    # print all the ruleitems in the set
    def print(self):
        for item in self.rule_set:
            item.print_ruleitem()


class CAR:
    """
    set of Class Association Rules 
    """
    def __init__(self):
        self.car_rule_set = set()
        self.pruned_car_rules = set()

    # print all the kept car rules
    def print_car_rules(self):
        for item in self.car_rule_set:
            item.print_rule() 

    # print all the pruned car rules
    def print_pruned_car_rules(self):
        for item in self.pruned_car_rules:
            item.print_rule() 

    # add a new car rule
    def add_car_rule(self, rule_item, min_support, min_confidence):
        # basic requirement
        if rule_item.support >= min_support and rule_item.confidence >= min_confidence:
            # do not add if the rule is already in the car rule set
            if rule_item in self.car_rule_set:
                return
            # save the ruleitem with the highest confidence when having the same condset
            for item in self.car_rule_set:
                if item.condset == rule_item.condset and item.confidence < rule_item.confidence:
                    self.car_rule_set.remove(item)
                    self.car_rule_set.add(rule_item)
                    return
                elif item.condset == rule_item.condset and item.confidence >= rule_item.confidence:
                    return
            self.car_rule_set.add(rule_item)

    # copy the frequent k-ruleitems set to car rule set
    def copy_freq_rules(self, frequentRIs, min_support, min_confidence):
        for item in frequentRIs.rule_set:
            self.add_car_rule(item, min_support, min_confidence)

    # prune rules from car set
    def prune_rules(self, data):
        for rule in self.car_rule_set:
            pruned_rule = prune(rule, data)

            is_in_set = False
            for rule in self.pruned_car_rules:
                if rule.label == pruned_rule.label:
                    if rule.condset == pruned_rule.condset:
                        is_in_set = True
                        break

            if not is_in_set:
                self.pruned_car_rules.add(pruned_rule)

    # add all the ruleitems from another car set
    def join(self, car, min_support, min_confidence):
        for item in car.car_rule_set:
            self.add_car_rule(item, min_support, min_confidence)


# *** need to consider more
def prune(rule, dataset):
    import sys
    min_rule_error = sys.maxsize
    pruned_rule = rule

    # prune rule recursively
    def find_prune_rule(this_rule):
        import cba_cb_m1  # *** change file name # import check_cover function
        nonlocal min_rule_error
        nonlocal pruned_rule

        # get number of errors: how many data cases do not cover the ruleitem
        def get_error_num(rule_item):
            error_num = 0
            for data_case in dataset:
                if cba_cb_m1.check_cover(data_case, rule_item) == False: # *** change file name
                    error_num += 1
            return error_num

        rule_error = get_error_num(this_rule)
        if rule_error < min_rule_error:
            min_rule_error = rule_error
            pruned_rule = this_rule
        this_rule_cond_set = list(this_rule.condset)
        if len(this_rule_cond_set) >= 2: # do not need to prune rules with 1 attribute
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


# join 2 ruleitems to generate a new candidate ruleitem
def join(r1, r2, dataset):
    # 2 ruleItem shall have the same class label
    if r1.label != r2.label:
        return None
    r1_condset = set(r1.condset)
    r2_condset = set(r2.condset)
    # 2 ruleItem cannot be the same
    if r1_condset == r2_condset:
        return None
    # same attribute should have the same value
    shared_attributes = r1_condset & r2_condset
    for col in shared_attributes:
        if r1.condset[col] != r2.condset[col]:
            return None
    # join 2 ruleItems
    combined_attributes = r1_condset | r2_condset
    new_condset = dict()
    for col in combined_attributes:
        if col in r1_condset:
            new_condset[col] = r1.condset[col]
        else:
            new_condset[col] = r2.condset[col]
    # generate new ruleitem
    new_ruleitem = ruleitem.RuleItem(new_condset, r1.label, dataset)
    return new_ruleitem


# similar to Apriori-gen in algorithm Apriori
def candidateGen(frequentRIs, dataset):
    results = FrequentRISet()
    for r1 in frequentRIs.rule_set:
        for r2 in frequentRIs.rule_set:
            new_ruleitem = join(r1, r2, dataset)
            if new_ruleitem: # not null
                results.add(new_ruleitem)
                #if returned_frequentRIs.get_num() >= 1000: # *** DELETE
                    #return returned_frequentRIs
    return results


# main function to run the rule generator
def rule_generator(dataset, min_support, min_confidence):
    new_frequentRIs = FrequentRISet()
    new_car = CAR()

    # get large 1-ruleitems and generate car_rule_set
    label_set = set([x[-1] for x in dataset]) # set of all lables for each data
    for column in range(0, len(dataset[0])-1):
        value_set = set([x[column] for x in dataset]) # set of all values under a column for each data
        for value in value_set:
            condset = {column: value}
            for label in label_set:
                rule_item = ruleitem.RuleItem(condset, label, dataset) # all possible 1-ruleitems
                if rule_item.support >= min_support:
                    new_frequentRIs.add(rule_item)
    new_car.copy_freq_rules(new_frequentRIs, min_support, min_confidence)
    # stores all the car 1-ruleitems
    all_cars = new_car
    # does not need to prune here because there is only one attribute in the condset

    current_cars_number = len(all_cars.car_rule_set) # cannot exceed 80000
    while new_frequentRIs.get_num() > 0 and current_cars_number <= 80000: # same ristriction as the paper
        candi_FreqRIs = candidateGen(new_frequentRIs, dataset)
        new_frequentRIs = FrequentRISet()
        new_car = CAR()
        # add the candidate ruleitems that meet the basic requirements
        for item in candi_FreqRIs.rule_set:
            if item.support >= min_support:
                new_frequentRIs.add(item)
        new_car.copy_freq_rules(new_frequentRIs, min_support, min_confidence)
        all_cars.join(new_car, min_support, min_confidence)
        current_cars_number = len(all_cars.car_rule_set)

    return all_cars


# just for test
if __name__ == "__main__":
    dataset = [[1, 1, 1], [1, 1, 1], [1, 2, 1], [2, 2, 1], [2, 2, 1],
               [2, 2, 0], [2, 3, 0], [2, 3, 0], [1, 1, 0], [3, 2, 0]]
    minsup = 0.15
    minconf = 0.6
    cars = rule_generator(dataset, minsup, minconf)

    print("CARs:")
    cars.print_rule()

    print("prCARs:")
    cars.prune_rules(dataset)
    cars.print_pruned_car_rules()
