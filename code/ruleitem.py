class RuleItem: 
    """ 
    Build the class RuleItem, including condset, class label y, condsupCount, rulesupCount, support and confidence. 
    Input: condset which include a set of items, label and the data_list.
    Output: a ruleitem with the value of condsupCount, rulesupCount, support and confidence. 
    """
    def __init__(self, condset, label, data_list):
        """ According to the paper, each frequent k-ruleitems consists of the following:
        condset: a dictiondary that has key-value pair {"item name: value, item name: value...},
        where the item name are name of the column attributes.
        condsupCount: the support count of condset
        rulesupCount: the support count of the ruleitem
        y : the class label """
        self.condset = condset
        self.label = label
        self.condsupCount, self.rulesupCount = self.calculate_supCount(data_list)
        self.confidence = self.calculate_confidence()
        self.support = self.calculate_support(data_list)


    def calculate_supCount(self, data_list):
        """ Count the condsupCount and rulesupCount respectively. """
        # Initialization
        condsupCount = 0
        rulesupCount = 0
        # iterate through every data_list
        for data in data_list:
            # Initialization check condition to be true
            covered = True
            # inner interation 
            for index in self.condset:
                # if the value of condset and data at the same index position is different
                if self.condset[index] != data[index]:
                    # there is nothing to count
                    covered = False
                    break
            # if the value are the same at the same index position
            if covered:
                # value of condsupCount + 1
                condsupCount += 1
                # if they belong to the same label class
                if self.label == data[-1]:
                    # rulesupCpunt + 1
                    rulesupCount += 1
        return condsupCount, rulesupCount
        
    
    def calculate_confidence(self):
        """ Calculate the confidence. """
        if self.condsupCount == 0:
            return 0
        else:
            # by formula
            return self.rulesupCount / self.condsupCount


    def calculate_support(self, data_list):
        """ Calculate the support. """
        # find the total data size
        data_list_size = len(data_list)
        support = self.rulesupCount / data_list_size
        return support





