import discretization
import readfile

# Obtain the mode value for a column of data list
# Used for missing value 
def find_mode(column_data):
	""" Identify the mode of a numderical or categorical column
		If there are more than 1 mode values having the same frequency
		return the first one as mode
		columns_data: a list column_data to find the mode """
	mode = []
	# count number of times each data shown
	# the key is the value of data, value is it's respective frequency
	data_frequency = dict((data, column_data.count(data)) for data in column_data)  
	# get the max_frequency for the column
	max_frequency = max(data_frequency.values())
	# if max frequency is 1, means all data showed up for the same number of times
	if max_frequency == 1:      
		print("no mode")
		return None
	else:
		for key, value in data_frequency.items():     
			# if the frequency is the same as maximum frequency
			if value == max_frequency:
				mode.append(key)
	return mode[0]  # return first number if has many modes


# Replace data that have missing value with the mode value of the column
def replace_missing_values(data_list, column):
	""" Replace the '?' in missing value with the mode value of the column
		data_list: the data list returned after reading the file
		column: the index number of the column that have missing value """
	# get the number of row in data_list
	num_of_row = len(data_list)
    # get the data in each column
	column_data = [x[column] for x in data_list]    
	mode = find_mode(column_data)
    # interate through each row within the same column
	for row in range(num_of_row):
		# if there's missing value
		if data_list[row][column] == '?':
			# replace the '?' with the mode value of the column
			data_list[row][column] = mode              
	return data_list


# Retrive the two columns of data for discretization
# Combine the two columns
def find_discretization_data(numerical_data_column, label_column):
	""" Get the two columns of data that are needed to do discretization
		continuous_data_column: the data column that has numerical value
		label_column: the class label column """
	num_of_row = len(numerical_data_column) 
	discretization_data = []
    # iterate through each row
	for row in range(num_of_row):
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
	num_of_row = len(data_list)
	split_point_size = len(split_points)
	for row in range(num_of_row):
		# if the data > the last boundary
		if data_list[row][column] > split_points[split_point_size - 1]:
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
    num_of_row = len(data_list)
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
    for row in range(num_of_row):
        # assign the classes index to its respective categorical class
        data_list[row][column] = classes_index[data_list[row][column]] 
    return data_list, classes_index



"""# Discard all the column with its column_no in discard_list
# data: original data set
# discard_list: a list of column No. of the columns to be discarded
def discard(data, discard_list):
    size = len(data)
    length = len(data[0])
    data_result = []
    for i in range(size):
        data_result.append([])
        for j in range(length):
            if j not in discard_list:
                data_result[i].append(data[i][j])
    return data_result """


# This is the main function in this file
def preprocessing_main(data, attributes, attribute_types):
    """ The main function in this python file.
        data: the original list of data returned from readDataFile.read_files()
        attributes: the list of attribute in the data
        attribute_types: the respective data type of the attribute """
    num_of_column = len(data[0])
    num_of_row = len(data)
    label_column = [x[-1] for x in data]
    # iterate through each attribute column in the data
    for column in range(num_of_column - 1):
        data_column = [x[column] for x in data]
        """discard_list = []
        while (column < column_num):
        data_column = [x[i] for x in data]
        # process missing values
        missing_values_ratio = data_column.count('?') / size
        if missing_values_ratio > 0.5:
            discard_list.append(i)
            continue
        elif missing_values_ratio > 0:
            data = fill_missing_values(data, i)
            data_column = [x[i] for x in data]"""
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
                split_points.append(min_value + 2 * step)
            # print out the split points of the data
            print(attributes[column] + ", split points:", split_points)       
            data = complete_discretization(data, column, split_points)
        # if the type of data column is categorical
        elif attribute_types[column] == 'categorical':
            data, classes_index = replace_with_integer(data, column)
            # print out the classes and their assigned positive integer value
            print("Categorical atribute with new values:", attributes[column] + ":", classes_index)   

    """# discard
    if len(discard_list) > 0:
        data = discard(data, discard_list)
        print("discard:", discard_list)             # print out discard list"""
        
    return data


# just for test
if __name__ == '__main__':    
    test_data_path = 'C:/Users/XPS/Desktop/Uni drives me crazy/Y3S1/CZ4032 Data Analytics and Mining/Data-Mining-Project-1/dataset/wine.data'
    test_names_path = 'C:/Users/XPS/Desktop/Uni drives me crazy/Y3S1/CZ4032 Data Analytics and Mining/Data-Mining-Project-1/dataset/wine.names'
    test_data, test_attributes, test_attributes_types = readfile.read_files(test_data_path, test_names_path)
    proprocessed_test_data = preprocessing_main(test_data, test_attributes, test_attributes_types)


   
