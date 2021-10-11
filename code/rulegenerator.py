"""
Rule Generator:
Input: preprocessed data, minimum support and minimum confidence
Output: Class Association Rules (CARs)
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
    # add the CARs_rule from another FrequentRISet
    def append(self, new_set):
        for item in new_set.frequent_ruleitems:
            self.add(item)

    # print all the ruleitems in the set
    def print(self):
        for item in self.rule_set:
            item.print_ruleitem()


class CARs:
    """
    set of Class Association Rules 
    """
    def __init__(self):
        self.CARs_rule = set()
        self.pruned_CARs = set()

    # print all the kept car rules
    def print_CARs(self):
        for item in self.CARs_rule:
            item.print_rule() 

    # print all the pruned CARs rules
    def print_pruned_CARs(self):
        for item in self.pruned_CARs:
            item.print_rule() 

    # add a new CARs rule
    def add_car_rule(self, rule_item, min_support, min_confidence):
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

    # copy the frequent k-ruleitems set to CARs rule set
    def copy_freq_rules(self, frequentRIs, min_support, min_confidence):
        for item in frequentRIs.rule_set:
            self.add_car_rule(item, min_support, min_confidence)

    # prune rules from CARs set
    def prune_rules(self, data):
        for rule in self.CARs_rule:
            pruned_rule = pruning(rule, data)

            is_in_set = False
            for rule in self.pruned_CARs:
                if rule.label == pruned_rule.label:
                    if rule.condset == pruned_rule.condset:
                        is_in_set = True
                        break

            if not is_in_set:
                self.pruned_CARs.add(pruned_rule)

    # add all the ruleitems from another CARs set
    def join(self, CARs, min_support, min_confidence):
        for item in CARs.CARs_rule:
            self.add_car_rule(item, min_support, min_confidence)


# *** need to consider more
def pruning(rule, data_list):
    import sys
    min_rule_error = sys.maxsize
    pruned_rule = rule

    # prune rule recursively
    def find_prune_rule(this_rule):
        import CBA_CB_M1  # *** change file name # import check_cover function
        nonlocal min_rule_error
        nonlocal pruned_rule

        # get number of errors: how many data cases do not cover the ruleitem
        def get_error_num(rule_item):
            error_num = 0
            for data_line in data_list:
                if CBA_CB_M1.check_cover(data_line, rule_item) == False: # *** change file name
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
                temp_rule = ruleitem.RuleItem(temp_cond_set, this_rule.label, data_list)
                temp_rule_error = get_error_num(temp_rule)
                if temp_rule_error <= min_rule_error:
                    min_rule_error = temp_rule_error
                    pruned_rule = temp_rule
                    if len(temp_cond_set) >= 2:
                        find_prune_rule(temp_rule)

    find_prune_rule(rule)
    return pruned_rule


# join 2 ruleitems to generate a new candidate ruleitem
def join(r1, r2, data_list):
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
    new_ruleitem = ruleitem.RuleItem(new_condset, r1.label, data_list)
    return new_ruleitem


# similar to Apriori-gen in algorithm Apriori
def candidateGen(frequentRIs, data_list):
    results = FrequentRISet()
    for r1 in frequentRIs.rule_set:
        for r2 in frequentRIs.rule_set:
            new_ruleitem = join(r1, r2, data_list)
            if new_ruleitem: # not null
                results.add(new_ruleitem)
                #if returned_frequentRIs.get_num() >= 1000: # *** DELETE
                    #return returned_frequentRIs
    return results


# main function to run the rule generator
def rule_generator_main(data_list, min_support, min_confidence):
    new_frequentRIs = FrequentRISet()
    new_car = CARs()

    # get large 1-ruleitems and generate CARs_rule
    label_set = set([x[-1] for x in data_list]) # set of all lables for each data
    for column in range(0, len(data_list[0])-1):
        value_set = set([x[column] for x in data_list]) # set of all values under a column for each data
        for value in value_set:
            condset = {column: value}
            for label in label_set:
                rule_item = ruleitem.RuleItem(condset, label, data_list) # all possible 1-ruleitems
                if rule_item.support >= min_support:
                    new_frequentRIs.add(rule_item)
    new_car.copy_freq_rules(new_frequentRIs, min_support, min_confidence)
    # stores all the CARs 1-ruleitems
    all_cars = new_car
    # does not need to prune here because there is only one attribute in the condset

    current_cars_number = len(all_cars.CARs_rule) # cannot exceed 80000
    while new_frequentRIs.get_num() > 0 and current_cars_number <= 80000: # same ristriction as the paper
        candi_FreqRIs = candidateGen(new_frequentRIs, data_list)
        new_frequentRIs = FrequentRISet()
        new_car = CARs()
        # add the candidate ruleitems that meet the basic requirements
        for item in candi_FreqRIs.rule_set:
            if item.support >= min_support:
                new_frequentRIs.add(item)
        new_car.copy_freq_rules(new_frequentRIs, min_support, min_confidence)
        all_cars.join(new_car, min_support, min_confidence)
        current_cars_number = len(all_cars.CARs_rule)

    return all_cars


# just for test
if __name__ == "__main__":
    import readfile
    import preprocessing
    
    test_data_path = 'C:/Users/XPS/Desktop/Uni drives me crazy/Y3S1/CZ4032 Data Analytics and Mining/Data-Mining-Project-1/dataset/zoo.data'
    test_names_path = 'C:/Users/XPS/Desktop/Uni drives me crazy/Y3S1/CZ4032 Data Analytics and Mining/Data-Mining-Project-1/dataset/zoo.names'
    data_list = readfile.read_data_file(test_data_path)
    data_list, test_attributes, test_attribute_types = readfile.read_files(test_data_path, test_names_path)
    data_list = preprocessing.preprocessing_main(data_list, test_attributes, test_attribute_types)

    minsup = 0.1
    minconf = 0.5
    CARs = rule_generator_main(data_list, minsup, minconf)

    print("CARs:")
    CARs.print_CARs()

    print("CARs after pruning:")
    CARs.prune_rules(data_list)
    CARs.print_pruned_CARs()
