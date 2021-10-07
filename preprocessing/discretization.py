import math

class DataBlock:
	def __init__(self, data):
		""" Define a block to be split
		It consists of 4 members:
		data: the data table with a column of continuous-valued attribute and a column of class label;
            size: number of data case in this table;
            number_of_classes: the number of distinct class in this table;
            entropy: calculated entropy of dataset. """
		self.data = data
		self.size = len(data)
		# get distinct class labels in the data
		labels = set([x[1] for x in data]) 
		# get the number of classes    
		self.label_size = len(set(labels)) 
		# call the calculate entropy function
		self.entropy = calculate_entropy(data)  


def calculate_entropy(data):
    """ Calculate the entropy of dataset
    parameter data: the data table to be used. """
    data_size = len(data)
    labels = set([x[1] for x in data])
    # a dictionary with class label and it's count
    label_count = dict([(label, 0) for label in labels]) 
    for data_case in data:
		# count the number of data case for each class label
        label_count[data_case[1]] += 1              
    entropy = 0
    for label in labels:
        probability = label_count[label] / data_size
        # calculate information entropy by its formula, where the base of log is 2
        entropy = entropy - probability * math.log2(probability)         
    return entropy


def calculate_entropy_gain(original_datablock, left_datablock, right_datablock):
    """ Calcullaye Gain(A, T: S) mentioned in Dougherty, Kohavi & Sahami (1995), i.e. entropy gained by splitting original_block
        into left_block and right_block
        original_block: the block before partition
        left_block: the block split which its value below boundary
        right_block: the block above boundary
        Gain(A, T; S) = Ent(S) - E(A, T; S) """
    original_entropy = original_datablock.entropy 
    E_ATS = ((left_datablock.size / original_datablock.size) * left_datablock.entropy +
            (right_datablock.size / original_datablock.size) * right_datablock.entropy)
    entropy_gain = original_entropy - E_ATS
    return entropy_gain


def calculate_minimum_gain(original_datablock, left_datablock, right_datablock):
    """ Get minimum entropy gain required for a split of original_block into 2 blocks "left" and "right"
        as seen in Dougherty, Kohavi & Sahami (1995)
        original_block: the block before partition
        left_block: the block split which its value below boundary
        right_block: the block above boundary. """
    subtractor = math.log2(math.pow(3, original_datablock.label_size) - 2) 
    minuend = (original_datablock.label_size * original_datablock.entropy -
             left_datablock.label_size * left_datablock.entropy -
             right_datablock.label_size * right_datablock.entropy)
    delta = subtractor - minuend
    # calculate the minimum entropy gain required based on the formula
    minimum_gain = (math.log2(original_datablock.size - 1) / original_datablock.size) + (delta / original_datablock.size)
    return minimum_gain


def binary_split(original_datablock):
    """ Identify the best acceptable value to split the datablock
        datablock: a block of dataset
        Return value: a list of (boundary, entropy gain, left datablock, right datablock) or
        Return "None" when it's unnecessary to split. """
    # create a list of values that have the potential to be splitting boundary    
    candidates_boundaries = [x[0] for x in original_datablock.data] 
    # get distinct values in the list    
    candidates_boundaries = list(set(candidates_boundaries)) 
    # sort the values in ascending order        	
    candidates_boundaries.sort()  
    # remove the smallest value, because by definition no value is smaller                         
    candidates_boundaries = candidates_boundaries[1:]                 

	# split_point will be used to store sorted final boundary
    split_point = []     
    # test every cantidate if the entropy gain has met the minimum requirement  
    for value in candidates_boundaries:        
        # split the data block into 2 parts, left & right data block
        left = []
        right = []
        # split by data case into 2 groups, below & above the value
        for data in original_datablock.data:
            if data[0] < value:
                left.append(data)
            else:
                right.append(data)
        left_datablock = DataBlock(left)
        right_datablock = DataBlock(right)
		# calculate the entropy gain by splitting the datablock
        entropy_gain = calculate_entropy_gain(original_datablock, left_datablock, right_datablock)
        # calculate the minimum gain requirement
        minimum_requirement = calculate_minimum_gain(original_datablock, left_datablock, right_datablock)

        # if entropy gain is greater than or equal to the minimum gain requirement
        # the value is an acceptable candidate for boundary
        if entropy_gain >= minimum_requirement:
			 # append the list of value to the wall
            split_point.append([value, entropy_gain, left_datablock, right_datablock])  

    if split_point:    # is not empty
		# sort the value in aescending order by "entropy_gain"
        split_point.sort(key=lambda wall: wall[1]) 
        # return best value with maximum entropy gain  
        return split_point[-1]      
    else:
		# there's no need to split the data
        return None         



def complete_split(original_datablock):
    """ Recursively split a data block
		Append boundary obtained into 'split_points' in each iteration """
    split_points = []
    
    def recursive_split(original_datablock):
        """ inner recursive function, accumulate the partitioning values: walls """
        # binary partition, to get left and right datablock
        split_point = binary_split(original_datablock)        
        if split_point:        # there's a wall returned, dabablock can still can be spilt
			# record this partitioning value: the best candidate with maximum entropy gain
            split_points.append(split_point[0])    
            # recursively process the spllitting of left datablock  
            recursive_split(split_point[2])
            # recursively split right datablock   
            recursive_split(split_point[3])   
        else:
			# nothing to split, end of recursion
            return None                          
            
    recursive_split(original_datablock)
    # sort the boundaries in aescending order
    split_points.sort()                
    return split_points
    
    



