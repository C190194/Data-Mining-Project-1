import csv
import preprocessing

def convert_to_numerical(data_list, attribute_types):
	""" When the attribute type is numerical
		convert value from string to float.
		data_list: data list returned by read_data_file.
		attribute_types: list returned by read_names_file. """
	num_of_data = len(data_list)
	num_of_columns = len(data_list[1])
	attribute_columns = num_of_columns - 1
	for i in range(num_of_data):
		for j in range(attribute_columns):
			# when the column of attribute is of numerical type and there's no missing value
			if attribute_types[j] == 'numerical' and data_list[i][j] != '?':
				# covert the string to float type
				data_list[i][j] = float(data_list[i][j])
	return data_list


# Main function: read the whole dataset and convert into a list.
def read_files(data_path, names_path):
    """ filepath: directory of *.data file and *.name file. """
    # Read the file with *.data and get the data in every line
    # append the line in the data_list"""
    data_list = []
    with open(data_path, 'r') as data_file:
        lines = csv.reader(data_file, delimiter=',')
        for line in lines:
            data_list.append(line)
        while [] in data_list:
            data_list.remove([])
    
    # Read the file ending with *.names
    # return the list of data attributes and their value type
    def read_names_file(names_path):
        """ Read scheme file *.names and write down attribute names and value types.
            path: directory of *.names file. """
        with open(names_path, 'r') as csv_file:
            lines = csv.reader(csv_file, delimiter=',')
            # Read the first line to get attributes name
            attribute_names = next(lines) 
            # Read the second line to get the value type for each attributes 
            attribute_types = next(lines)  
            return attribute_names, attribute_types
    
    attribute_names, attribute_types = read_names_file(names_path)
    data_list = convert_to_numerical(data_list, attribute_types)
    return data_list, attribute_names, attribute_types
    

# Testing
if __name__ == '__main__':
    test_data_path = 'dataset/pima.data'
    test_names_path = 'dataset/pima.names'
    test_data, test_attributes, test_attribute_types = read_files(test_data_path, test_names_path)
    result_data = preprocessing.preprocessing_main(test_data, test_attributes, test_attribute_types)
    print(result_data)
