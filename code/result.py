import time
import random
from readfile import read_files
from preprocessing import preprocessing_main
from rulegenerator import rule_generator_main
from CBA_CB_M1 import check_cover
from CBA_CB_M2 import build_classifier_M2


def calculate_error_rate(classifier, data_list):
    """ Calculate the error rate of the classifier on the data_list used. """
    data_size = len(data_list)
    num_errors = 0
    # iterate through each data line in the data_list
    for data in data_list:
        is_covered = False
        # iterate through each rule in the rule_list
        for rule in classifier.rule_list:
            # check whether the rule correctly classify the data line
            is_covered = check_cover(data, rule)
            if is_covered == True:
                break
        # if the data is not covered by any rule in the rule_list
        if is_covered == False: 
            # and the data class label and default class label are different
            if classifier.default_label != data[-1]:
                num_errors += 1
    return num_errors / data_size


def cross_validattion_M2_without_pruning(data_path, names_path, minsup=0.01, minconf=0.5):
    """ 10-fold cross-validation on CBA-CB-M2 Classifier withought rule pruning. """
    data_list, attributes, attribute_types = read_files(data_path, names_path)
    random.shuffle(data_list)
    data_list = preprocessing_main(data_list, attributes, attribute_types)
    data_size = len(data_list)
    # validation_size = data_size / 10 as we are doing 10-fold cross validation
    validation_size = int(data_size / 10)
    # split point for 10 interval range
    split_point = [x * validation_size for x in range(0, 10)]
    # split the whole data_list into 10
    split_point.append(data_size)

    # Initialization
    rule_gengerator_totalt_runtime = 0
    M2_total_time = 0
    total_num_CARs = 0
    total_num_M2classifier_rules = 0
    total_error_rate = 0

    for k in range(len(split_point)-1):
        print("\nRound %d:" % k)
        # prepare training and testing data
        training_data = data_list[:split_point[k]] + data_list[split_point[k+1]:]
        testing_data = data_list[split_point[k]:split_point[k+1]]
        print("splitting done")

        # compute the single and total runtime for rule generator
        start_time = time.time()
        CARs = rule_generator_main(training_data, minsup, minconf)
        print("rule generator done")
        end_time = time.time()
        rule_gengerator_runtime = end_time - start_time
        rule_gengerator_totalt_runtime += rule_gengerator_runtime

        # compute the single and total runtime for classifier M2
        start_time = time.time()
        M2 = build_classifier_M2(CARs, training_data)
        end_time = time.time()
        M2_runtime = end_time - start_time
        M2_total_time += M2_runtime
        
        # compute the error rate and total error rate
        error_rate = calculate_error_rate(M2, testing_data)
        total_error_rate += error_rate
        
        # compute the total number of CARs generated 
        total_num_CARs += len(CARs.CARs_rule)
        # compute the total number of rules in the classifier
        total_num_M2classifier_rules += len(M2.rule_list)

        print("CBA-CB M2's error rate without rule pruning: %.1lf%%" % (error_rate * 100))
        print("No. of CARs generated without rule pruning: %d" % len(CARs.CARs_rule))
        print("CBA-RG's run time without rule pruning: %.2lf s" % rule_gengerator_runtime)
        print("CBA-CB M2's run time without rule pruning: %.2lf s" % M2_runtime)
        print("No. of rules in classifier of CBA-CB M2 without rule pruning: %d" % len(M2.rule_list))

    print("\nAverage CBA-CB M2's error rate without rule pruning: %.1lf%%" % (total_error_rate / 10 * 100))
    print("Average No. of CARs generated without rule pruning: %d" % int(total_num_CARs / 10))
    print("Average CBA-RG's run time without rule pruning: %.2lf s" % (rule_gengerator_totalt_runtime / 10))
    print("Average CBA-CB M2's run time without rule pruning: %.2lf s" % (M2_total_time / 10))
    print("Average No. of rules in classifier of CBA-CB M2 without rule pruning: %d" % int(total_num_M2classifier_rules / 10))
    
    

def cross_validation_M2_with_pruning(data_path, names_path, minsup=0.1, minconf=0.5):
    """ 10-fold cross-validation on CBA-CB-M2 Classifier with rule pruning. """
    data_list, attributes, attribute_types = read_files(data_path, names_path)
    random.shuffle(data_list)
    data_list = preprocessing_main(data_list, attributes, attribute_types)
    data_size = len(data_list)
    # validation_size = data_size / 10 as we are doing 10-fold cross validation
    validation_size = int(data_size / 10)
    # split point for 10 interval range
    split_point = [x * validation_size for x in range(0, 10)]
    # split the whole data_list into 10
    split_point.append(data_size)

    # Initialization    
    rule_generator_total_runtime = 0
    M2_total_time = 0
    total_num_CARs = 0
    total_num_M2classifier_rules = 0
    total_error_rate = 0

    for k in range(len(split_point)-1):
        print("\nRound %d:" % k)
        # prepare training and testing data
        training_data = data_list[:split_point[k]] + data_list[split_point[k+1]:]
        testing_data = data_list[split_point[k]:split_point[k+1]]
        
        # compute the single and total runtime for rule generator with rule pruning
        start_time = time.time()
        CARs = rule_generator_main(training_data, minsup, minconf)
        CARs.prune_rules(training_data)
        CARs.CARs_rule = CARs.pruned_CARs
        end_time = time.time()
        rule_gengerator_runtime = end_time - start_time
        rule_generator_total_runtime += rule_gengerator_runtime

        # compute the single and total runtime for classifier M2 with rule pruning
        start_time = time.time()
        M2_pruning = build_classifier_M2(CARs, training_data)
        end_time = time.time()
        M2_runtime = end_time - start_time
        M2_total_time += M2_runtime

        # compute the error rate and total error rate
        error_rate = calculate_error_rate(M2_pruning, testing_data)
        total_error_rate += error_rate

        # compute the total number of CARs generated 
        total_num_CARs += len(CARs.CARs_rule)
        # compute the total number of rules in the classifier
        total_num_M2classifier_rules += len(M2_pruning.rule_list)

        print("CBA-CB M2's error rate with rule pruning: %.1lf%%" % (error_rate * 100))
        print("No. of CARs generated with rule pruning: %d" % len(CARs.CARs_rule))
        print("CBA-RG's run time with rule pruning: %.2lf s" % rule_gengerator_runtime)
        print("CBA-CB M2's run time with rule pruning: %.2lf s" % M2_runtime)
        print("No. of rules in classifier of CBA-CB M2 with rule pruning: %d" % len(M2_pruning.rule_list))

    print("\nAverage CBA-CB M2's error rate with rule pruning: %.1lf%%" % (total_error_rate / 10 * 100))
    print("Average No. of CARs generated with rule pruning: %d" % int(total_num_CARs / 10))
    print("Average CBA-RG's run time with rule pruning: %.2lf s" % (rule_generator_total_runtime / 10))
    print("Average CBA-CB M2's run time with rule pruning: %.2lf s" % (M2_total_time / 10))
    print("Average No. of rules in classifier of CBA-CB M2 with rule pruning: %d" % int(total_num_M2classifier_rules / 10))


# test entry goes here
if __name__ == "__main__":
    # using the relative path, all data sets are stored in datasets directory
    test_data_path = 'C:/Users/XPS/Desktop/Uni drives me crazy/Y3S1/CZ4032 Data Analytics and Mining/Data-Mining-Project-1/dataset/zoo.data'
    test_names_path = 'C:/Users/XPS/Desktop/Uni drives me crazy/Y3S1/CZ4032 Data Analytics and Mining/Data-Mining-Project-1/dataset/zoo.names'

    cross_validattion_M2_without_pruning(test_data_path, test_names_path)
    #cross_validation_M2_with_pruning(test_data_path, test_names_path)





