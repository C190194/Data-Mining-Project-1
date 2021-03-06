import discretization
import readfile

# Retrive the two columns of data for discretization
# Combine the two columns
def find_discretization_data(numerical_data_column, label_column):
	""" Get the two columns of data that are needed to do discretization
		continuous_data_column: the data column that has numerical value
		label_column: the class label column """
	num_rows = len(numerical_data_column) 
	discretization_data = []
    # iterate through each row
	for row in range(num_rows):
		# combine the data in the list
		discretization_data.append([numerical_data_column[row], label_column[row]])
	return discretization_data


# Assign new value to the column of data after discretization
# The new value will be the index of interval the original value belongs to
def complete_discretization(data_list, column, split_points):
	""" Replace numerical data value with the index of splitting interval obtained by discretization.py
		data_list: the data list returned from reading the data file
		column: the index of the data column that have numerical data value
		split_points: the list of splitting boundary """
	num_rows = len(data_list)
	split_point_size = len(split_points)
	for row in range(num_rows):
		# if the data > the last boundary
		if data_list[row][column] > split_points[split_point_size-1]:
			# assign the new value to be the index of the last interval
			data_list[row][column] = split_point_size + 1
        # iterate through each splliting point 
		i = 0
		while (i < split_point_size):
			# if the data is within the interval
			if data_list[row][column] <= split_points[i]:
				# assin new value as the index of the interval
				data_list[row][column] = i + 1
				break
			i += 1
	return data_list


# Replace the values of categorical data with a positive integer.
def replace_with_integer(data_list, column):
    """ Replace the value of categorical data with a positive integer.
        data_list: the data list returned from reading the data file
        column: the index of the categorical data column """
    num_rows = len(data_list)
    # get distinct categorical classes in the data column
    categorical_classes = set([x[column] for x in data_list]) 
    # a dictionary of each dinstinct categorical class
    # the value of the dictionary will be used as the positve integer assiged to the categorical data
    classes_index = dict([(c, 0) for c in categorical_classes]) 
    index = 1 
    for c in categorical_classes:
        # increase the classes_index by 1 as we only assign positive integer
        # the index start at 1
        classes_index[c] = index
        index += 1
    for row in range(num_rows):
        # assign the classes index to its respective categorical class
        data_list[row][column] = classes_index[data_list[row][column]] 
    return data_list, classes_index


# This is the main function in this file
def preprocessing_main(data, attributes, attribute_types):
    """ The main function in this python file.
        data: the original list of data returned from readDataFile.read_files()
        attributes: the list of attribute in the data
        attribute_types: the respective data type of the attribute """
    num_columns = len(data[0])
    num_rows = len(data)
    label_column = [x[-1] for x in data]
    discard_list = []
    # iterate through each attribute column in the data
    for column in range(num_columns - 1):
        data_column = [x[column] for x in data]
        # discretization
        # if the type of data column is numerical
        if attribute_types[column] == 'numerical':
            discretization_data = find_discretization_data(data_column, label_column)
            datablock = discretization.DataBlock(discretization_data)
            split_points = discretization.complete_split(datablock)
            # if there are no split points return
            if len(split_points) == 0:
                max_value = max(data_column)
                min_value = min(data_column)
                interval = (max_value - min_value) / 3
                split_points.append(min_value + interval)
                split_points.append(min_value + 2 * interval)
            # print out the split points of the data
            print(attributes[column] + ", split points:", split_points)       
            data = complete_discretization(data, column, split_points)
        # if the type of data column is categorical
        elif attribute_types[column] == 'categorical':
            data, classes_index = replace_with_integer(data, column)
            # print out the classes and their assigned positive integer value
            print("Categorical atribute with new values:", attributes[column] + ":", classes_index) 
    print("The number of distict class label in the dataset is:", len(set(label_column)))  
    print("Total number of attributes in the dataset: ", num_columns-1)        
    return data


# Testing
if __name__ == '__main__':    
    test_data_path = 'dataset/iris.data'
    test_names_path = 'dataset/iris.names'
    test_data, test_attributes, test_attributes_types = readfile.read_files(test_data_path, test_names_path)
    proprocessed_test_data = preprocessing_main(test_data, test_attributes, test_attributes_types)
    print(proprocessed_test_data)

   
