import cba_rg
from functools import cmp_to_key
import sys


def check_cover(data_line, rule):
    """ Check whether the rule covers a single line in the data_list,
    the line is each row in the original data_list """
    for item in rule.cond_set:
        # check if  the dataline and the LHS of the rule are the same
        # if different, return None
        if dataline[item] != rule.cond_set[item]:
            return None
    # if same and they belong to the same class label, return ture
    if data_line[-1] == rule.class_label:
        return True
    # else return false
    else:
        return False


class Classifier_M1:
    """
    Build the class for classifier. 
    The rule_list and default_class are useful for outer code.
    """
    def __init__(self):
        self.rule_list = list()
        self.error_list = list()
        self.default_label = None
        self.default_label_list = list()

    def rule_insertion(self, rule, data_list):
        """ Insert a single rule into rule_list.
        Choose a default label from the current dataset.
        And compute the error to append in error_list in future. """
        # append the rule at the end of the rule_list
        self.rule_list.append(rule)            
        # select the default label from the current data_list
        self.default_label_selection(data_list)  
        # count the total number of errors in the data_list 
        self.count_errors(data_list)            


    def default_label_selection(self, data_list):
        """ Find the label that has the highest frequency as the default label"""
        # the last column is the label column
        label_column = [x[-1] for x in data_list]
        # find distinct labels
        labels = set(label_column)
        max_count = 0
        default_label = None
        for label in labels:
            if label_column.count(label) >= max_count:
                max_count = label_column.count(label)
                default_label = label
        self.default_label_list.append(default_label)

    # count the total number of errors
    def count_errors(self, data_list):
        """ calculate the sum of errors. """
        # if the length of data_list is equal or smaller than 0
        if len(data_list) <= 0:
            self.error_list.append(sys.maxsize)
            return None
            
        # initiate the number of errors as 0
        num_errors = 0

        # count the number of errors made by all the selected rules in data_list
        for data in data_list:
            # Initiation
            cover = False
            for rule in self.rule_list:
                if check_cover(data, rule):
                    cover = True
                    break
            if not cover:
                # if the rule does not cover the data, that count as an error
                num_errors += 1

        # the number of errors to be made by the default class in the training set
        label_column = [x[-1] for x in data_list]
        # calculate the number of errors that will be made by the default label
        additional_errors = len(label_column) - label_column.count(self.default_label_list[-1])
        num_errors += additional_errors
        self.error_list.append(num_errors)

    # see line 14 and 15, to get the final classifier
    def rule_cleaning(self):
        """ Find the rule with the minimum number of erros.
        Drop all the remaining rules after that rule. """
        # find the minimum number of errors in the list
        min_errors = min(self.error_list)
        # fine the rule's index position
        position = self.error_list.index(min_errors)
        # discard all the rules after
        self.rule_list = self.rule_list[:(position+1)]
        self.error_list = None

        # assign the default label 
        # to be the label at the same position index as the rule in the default_label_list
        self.default_label = self.default_label_list[position]
        self.default_label_list = None


    def print(self):
        """ A print function that print out all the selected rules 
        and default class label in the classifier. """
        for rule in self.rule_list:
            rule.print_rule()
        print("Default class label:", self.default_label)


def sort_CARs(car):
    """ Sort the list of generated class association rules in descending order.
    The order is based on the relation ">" in precendence.
    Return the sorted rule list. """
    def compare_rules(r1, r2):
        """ Compare the rules in CARs based on the article.
        As we need to choose a set of high precedence rules for the classifier. """
        if r2.confidence > r1.confidence:     # 1. the confidence of r2 > r1
            # r2 have higher precendence than r1, meaning r2 > r1
            return 1
        elif r1.confidence == r2.confidence:
            if r2.support > r1.support:       # 2. confidence of r1 and r2 are the same, but support of r2 > r1
                return 1
            # if both support and confidence are the same
            elif r1.support == r2.support:
                if len(r1.cond_set) < len(r2.cond_set):   # 3. but r1 is generated earlier than r2
                    # r1 have a higher precedence than r2, r1 > r2
                    return -1
                elif len(a.cond_set) == len(b.cond_set):
                    return 0
                else:
                    return 1
            else:
                return -1
        else:
            return -1

    rule_list = list(car.rules)
    # sort the list of generated CARs
    rule_list.sort(key=cmp_to_key(compare_rules))
    return rule_list


# main method of CBA-CB: M1
def classifier_builder_m1(cars, dataset):
    classifier = Classifier()
    cars_list = sort(cars)
    for rule in cars_list:
        temp = []
        mark = False
        for i in range(len(dataset)):
            is_satisfy_value = is_satisfy(dataset[i], rule)
            if is_satisfy_value is not None:
                temp.append(i)
                if is_satisfy_value:
                    mark = True
        if mark:
            temp_dataset = list(dataset)
            for index in temp:
                temp_dataset[index] = []
            while [] in temp_dataset:
                temp_dataset.remove([])
            dataset = temp_dataset
            classifier.insert(rule, dataset)
    classifier.discard()
    return classifier


# just for test
if __name__ == '__main__':
    dataset = [[1, 1, 1], [1, 1, 1], [1, 2, 1], [2, 2, 1], [2, 2, 1],
               [2, 2, 0], [2, 3, 0], [2, 3, 0], [1, 1, 0], [3, 2, 0]]
    minsup = 0.15
    minconf = 0.6
    cars = cba_rg.rule_generator(dataset, minsup, minconf)
    classifier = classifier_builder_m1(cars, dataset)
    classifier.print()

    print()
    dataset = [[1, 1, 1], [1, 1, 1], [1, 2, 1], [2, 2, 1], [2, 2, 1],
               [2, 2, 0], [2, 3, 0], [2, 3, 0], [1, 1, 0], [3, 2, 0]]
    cars.prune_rules(dataset)
    cars.rules = cars.pruned_rules
    classifier = classifier_builder_m1(cars, dataset)
    classifier.print()
