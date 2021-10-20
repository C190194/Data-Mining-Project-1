import readfile
import preprocessing

import new_FP_Tree
import new_CR_Tree
import new_Classifier

import random
import time


def run_FP_classification(data_path, names_path, min_sup, min_conf, coverage_threshold):
    """ 10-fold cross-validation on CBA-CB-M2 Classifier with rule pruning. """
    data_list, attributes, attribute_types = readfile.read_files(data_path, names_path)
    random.shuffle(data_list)
    data_list = preprocessing.preprocessing_main(data_list, attributes, attribute_types)
    data_size = len(data_list)
    # validation_size = data_size / 10 as we are doing 10-fold cross validation
    validation_size = int(data_size / 10)
    # split point for 10 interval range
    split_point = [x * validation_size for x in range(0, 10)]
    # split the whole data_list into 10
    split_point.append(data_size)

    # Initialization
    rule_gengerator_total_runtime = 0
    total_num_rules = 0
    total_error_rate = 0

    for k in range(len(split_point) - 1):

        print("\nRound %d:" % k)
        # prepare training and testing data
        training_data = data_list[:split_point[k]] + data_list[split_point[k + 1]:]
        testing_data = data_list[split_point[k]:split_point[k + 1]]

        # compute the single and total runtime for rule generator with rule pruning
        start_time = time.time()
        new_min_sup = min_sup * len(training_data)
        print(min_sup)
        f_list= new_FP_Tree.ordered_F_list(training_data, new_min_sup)
        FP_tree_root, FP_header_table = new_FP_Tree.create_FP_tree(training_data, f_list)
        temp_CR_tree_root = new_FP_Tree.rule_generator(f_list, FP_header_table, new_min_sup, min_conf, training_data)
        CRTroot, CR_header_table, num_rules = new_CR_Tree.last_pruning(temp_CR_tree_root, coverage_threshold, training_data)
        end_time = time.time()
        rule_gengerator_runtime = end_time - start_time
        rule_gengerator_total_runtime += rule_gengerator_runtime

        # compute the error rate and total error rate
        class_sup_dic, training_data_size = new_Classifier.class_sup_preprocess(training_data)
        num_errors = 0
        data_size = len(testing_data)
        for row in testing_data:
            label = new_Classifier.classify(row[:-1:], CRTroot, class_sup_dic, training_data_size)
            if label != row[-1]:
                num_errors += 1
        error_rate = num_errors / data_size
        total_error_rate += error_rate

        # compute the total number of rules generated
        total_num_rules += num_rules

        print("CMAR's error rate: %.1lf%%" % (error_rate * 100))
        print("No. of rules generated: %d" % num_rules)
        print("CMAR's run time: %.2lf s" % rule_gengerator_runtime)

    print("\nAverage CMAR's error rate: %.1lf%%" % (total_error_rate / 10 * 100))
    print("Average No. of rules generated: %d" % int(total_num_rules / 10))
    print("Average CMAR's run time: %.2lf s \n" % (rule_gengerator_total_runtime / 10))

    return total_error_rate / 10 * 100, rule_gengerator_total_runtime / 10, int(total_num_rules / 10)


if __name__ == "__main__":
    # using the relative path, all data sets are stored in datasets directory
    # glass
    # wine
    # iris
    # pima
    # tic-tac-toe
    # caesarian
    # car
    f = "caesarian"
    data_path = 'dataset/' + f + '.data'
    names_path = 'dataset/' + f + '.names'
    # generate rules using the CMAR method
    min_sup = 0.01
    min_conf = 0.5
    coverage_threshold = 4

    # total_error_rate = 0
    # total_runtime = 0
    # total_num_rules = 0
    # for i in range(2):
    #     error_rate, runtime, num_rules = run_FP_classification(data_path, names_path, min_sup, min_conf, coverage_threshold)
    #     total_error_rate += error_rate
    #     total_runtime += runtime
    #     total_num_rules += num_rules
    # print("In " + f + " dataset:")
    # print("Average CMAR's error rate: %.1lf%%" % (total_error_rate / 2))
    # print("Average CMAR's accuracy: %.1lf%%" % (100 - (total_error_rate / 2)))
    # print("Average CMAR's run time: %.2lf s" % (total_runtime / 2))
    # print("Average CMAR's number of rules: %d \n" % (total_num_rules / 2))

    data_file_list = ["glass", "wine", "iris", "pima", "tic-tac-toe", "caesarian", "car"]
    result = {}
    for f in data_file_list:
        data_path = 'dataset/' + f + '.data'
        names_path = 'dataset/' + f + '.names'
        total_error_rate = 0
        total_runtime = 0
        total_num_rules = 0
        for i in range(2):
            error_rate, runtime, num_rules = run_FP_classification(data_path, names_path, min_sup, min_conf, coverage_threshold)
            total_error_rate += error_rate
            total_runtime += runtime
            total_num_rules += num_rules
        result[f] = (total_error_rate / 2, total_runtime / 2, total_num_rules / 2)

    for dataset_name, record in result.items():
        print("In " + dataset_name + " dataset:")
        print("Average CMAR's error rate: %.1lf%%" % record[0])
        print("Average CMAR's accuracy: %.1lf%%" % (100 - record[0]))
        print("Average CMAR's run time: %.2lf s" % record[1])
        print("Average CMAR's number of rules: %d \n" % record[2])
