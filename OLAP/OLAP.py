#!/usr/bin/env python3

# Libraries
import argparse
import os
import sys
import csv

def main():
    '''
        Initializes the argument parsing object for reading the command line inputs, initializes the DataBlock object for storing the input data from
        the passed input file, and calls the respective functions based on the input commands. Finally, calls the output function to output the manipulated
        data.
    '''

    # Initializing a parsing object for command line input
    argument_parser = argparse.ArgumentParser(description='Online Analytical Processing(OLAP) used for calculating min, max, mean(average), sum, and count of numerical columns. The group-by and top-k are used for categorical columns')

    # Adding arguments to parser object
    argument_parser.add_argument('--input', nargs='?') # Optional argument for input file
    argument_parser.add_argument('--sum', nargs='*', action=Organizer) # Optional argument for summing value(s)
    argument_parser.add_argument('--min', nargs='*', action=Organizer) # Optional argument for getting the minimum value(s)
    argument_parser.add_argument('--max', nargs='*', action=Organizer) # Optional argument for getting the maximum value(s)
    argument_parser.add_argument('--mean', nargs='*', action=Organizer) # Optional argument for getting the mean(average) value(s)
    argument_parser.add_argument('--count', nargs=0, action=Organizer) # Optional argument for counting the number of records
    argument_parser.add_argument('--top', nargs='*', action=Organizer) # Optional argument for getting the top k values
    argument_parser.add_argument('--groupby', '--group-by', nargs=1, default= -1) # Optional argument for grouping the output data

    # Parse the arguments
    arguments = argument_parser.parse_args()

    # Variables
    line_count = 0 # Line count tracker
    verify_file = '' # String variable to verify the input file extension

    # If only --input was put in the commmand line, add count
    if not 'order' in arguments:
        setattr(arguments, 'order', [])
        arguments.order.append(['count', []])

    # Getting the inputted file string
    verify_file = arguments.input

    # Checking if input file has a .csv extension
    if not verify_file.lower().endswith('.csv'):

        # Print on standard error
        print('Error: ' + verify_file + ' is not a CSV file, please check if file extension was inputted correctly.', file = sys.stderr)

        exit(6)
    
    # Create a DataBlock object
    data = DataBlock(arguments.input)

    # Open file passed by the input aggregate function
    with open(arguments.input, 'r', encoding='utf-8-sig') as csv_file:

        # Read a single line at a time from the file
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:

            if line_count < 1:

                data.add_header(row)

                line_count = 1

            else:

                data.add_data(row)
    
    # Check if group-by was passed and if it's argument is valid
    if arguments.groupby != -1 and arguments.groupby[0].lower() not in data.column_header:

        # Print on standard error
        print('Error: \'' + data.input + '\':no group-by argument with name \'' + arguments.groupby[0] + '\' found', file=sys.stderr)

        exit(9)
    
    # Checking the validity of passed fields
    for ele in arguments.order:

        # If ele is count, go to next iteration as count doesn't take a field
        if ele[0] == 'count':

            continue

        elif ele[0] == 'top':

            if ele[1][1].lower() not in data.column_header:

                # Print on standard error
                print('Error: \'' + data.input + '\':no field with name \'' + ele[1][1] + '\' found', file=sys.stderr)

                exit(8)

        else: 
            
            # Checking all other aggregate functions
            if ele[1][0].lower() not in data.column_header:

                # Print on standard error
                print('Error: \'' + data.input + '\':no field with name \'' + ele[1][0] + '\' found', file=sys.stderr)
                exit(8)
    
    # Checking if group-by was passed in command line
    if arguments.groupby != -1:

        # Variables
        groupby_data = [] # List to hold the data of group-by field

        # Finding the index location of the groupby_name parameter
        groupby_index = data.column_header.index(arguments.groupby[0].lower())

        # Fill temp_list with all the values from groupby_name column
        for i in range(len(data.column_data)):
            groupby_data.append(data.column_data[i][groupby_index])

        # Create a list of unique elements from temp_list
        groupby_header = [x for x in set(groupby_data)]
        
        # Sort in ascending order
        groupby_header.sort()

        result_data = data.column_group(arguments, arguments.groupby[0])

        output_results(arguments, result_data, groupby_header, data.top_capped, data.groupby_capped)

    else:

        # Variables
        result_data = [] # List for holding all the resulting data other than top k
        top_data = [] # List for holding top k's data

        # Call the respective functions based on elements in arguments.order
        for ele in arguments.order:

            if ele[0] == 'count':

                result_data.append([data.column_count()])
            
            elif ele[0] == 'sum':

                result_data.append([data.column_sum(ele[1][0])])
            
            elif ele[0] == 'min':

                result_data.append([data.column_min(ele[1][0])])

            elif ele[0] == 'max':

                result_data.append([data.column_max(ele[1][0])])

            elif ele[0] == 'mean':

                result_data.append([data.column_mean(ele[1][0])])
            
            elif ele[0] == 'top':

                top_data.extend(data.column_top(int(ele[1][0]), ele[1][1]))
        
        output_results(arguments, result_data, top_data, data.top_capped)


def output_results(result_header, result_data, groupby_list = None, top_capped = False, groupby_capped = False):
    """
        Outputs all the data to a csv file called output.csv

        Parameters
        ----------
        result_header : list
            All the arguments passed at the command line in order

        result_data : list
            All the data based on the arguments passed on the command line

        groupby_list : list, optional
            Containing the unique values that the data is grouped by (default is None)

        top_capped : boolean
            Indicating if top's data has been capped (default is False)

        groupby_capped : boolean
            Indicating if group-by has been capped (default is False)

    """

    # Variables for holding column titles for output
    min_title = 'min_'
    max_title = 'max_'
    mean_title = 'mean_'
    sum_title = 'sum_'
    top_title = 'top_'
    count_title = 'count'

    # List variables for holding the output header and data 
    output_header = []
    output_data = []
    
    # Checking if output will be in group-by format
    if result_header.groupby != -1:
        
        # Variable
        top_called = False # Flag for if top was called
        top_index = -1 # Integer for top's location

        for ele in result_header.order:

            if ele[0] == 'top':

                # Top was called
                top_called = True

                # Variables for splitting top's data from resulting data list
                top_list = [] # List that will solely hold top's data
                split_list = [] # List that will hold the left over data after top's has been extracted 

                # Setting the location index for top command
                top_index = result_header.order.index(ele)
                
                # Counter to track how many items from top have been added to ouput_data
                top_counter = 0

                # Splitting top's data from resulting data
                top_list.extend(result_data[top_index])

                for i in result_data:

                    # Get the index location of i
                    index = result_data.index(i)

                    # Checking if index is equal to top_index
                    if index == top_index:
                        continue
                    else:
                        split_list.append(result_data[index])

                    # End of for i in result_data:

                result_data = split_list
                break
                
                #End of if ele[0] == 'top':

            # End of or ele in result_header.order:
        
        # Setting groupby_field to field name passed to group-by
        groupby_field = result_header.groupby[0]

        output_header.append(groupby_field.lower())

        # Checking it top was called
        if top_called:
            
            for ele in  groupby_list:
                
                # Reset building_row each iteration
                building_row = []

                # Getting the index location of ele in groupby_list
                ele_index = groupby_list.index(ele)

                building_row.append(ele)
        
                for i in range(len(result_data)):

                    building_row.append(result_data[i][ele_index])

                    # End of for i in range(len(result_data)):

                # Checking if top_counter is less than the length of top_list
                if top_counter < len(top_list):

                    # Insert element from top_list into temp_list at location top_index + 1
                    building_row.insert(top_index+1, top_list[top_counter][0])

                    top_counter += 1

                else:

                    # This means that top_list is smaller than resulting data list
                    building_row.insert(top_index+1, None)

                # Creating a 2D list
                output_data.append(building_row)

                # End of for ele in  groupby_list:

            # Checking if top_counter is less than top_list
            # This check is only true if top_list has more data than result_data
            if top_counter < len(top_list):
                
                # Loop until top_counter is not less than length of top_list
                while top_counter < len(top_list):

                    # Reset building_row each iteration
                    building_row = []

                    # Building the reset of the rows
                    for i in range(len(result_data)):

                        # Checking if i value is equal to top_index + 1
                        if i == top_index + 1:

                            building_row.extend(top_list[top_counter])

                            top_counter += 1

                        else:

                            building_row.append(None)

                        # End of for i in range(len(result_data)):
                
                    output_data.append(building_row)

                    # End of while top_counter < len(top_list):

            # End of if top_called:
        else:
                
            # Creating output_data list
            for ele in  groupby_list:
                
                # Reset building_row each iteration
                building_row = []

                # Getting the index location of ele in groupby_list
                ele_index = groupby_list.index(ele)

                building_row.append(ele)
        
                for i in range(len(result_data)):

                    building_row.append(result_data[i][ele_index])

                    # End of for i in range(len(result_data)):
                
                # Creating a 2D list
                output_data.append(building_row)

                # End of for ele in  groupby_list:

        # End of if result_header.groupby != -1:
    else:
        # This code is for if no group-by was passed at command line

        # Checking if top k data was passed
        if groupby_list is not None:

            # Variables
            first_row = [] # Temporary list for bulding first row if output data
            top_index = -1 # Integer for holding the location of top if it was called

            # Result placement index
            result_index = 0

            # Checking if top was call on command line
            for ele in result_header.order:

                if ele[0] == 'top':

                    # Setting the location index for top command
                    top_index = result_header.order.index(ele)

                # End of for ele in result_header.order:

            # Building the first row of the output data by putting top's data in correct location
            for order_ele in range(len(result_header.order)):

                # Checking if order_ele is equal to top_index
                if order_ele == top_index:
                    first_row.extend(groupby_list[0])
                
                # Extending first_row list by a value from result_data
                if result_index < len(result_data):
                    first_row.extend(result_data[result_index])
                    result_index += 1

                # End of for order_ele in range(len(result_header.order)):

            output_data.append(first_row)

            # Building the rest of the rows for top k data
            for row_data in range(1,len(groupby_list)):

                # Reset building_row to be empty each iteration
                building_row = []

                for placement in range(len(result_header.order)):

                    # Checking if placement is equal to top_index
                    if placement != top_index:
                        building_row.append(None)
                    else:
                        building_row.append(groupby_list[row_data][0])

                    # End of for placement in range(len(result_header.order)):
                    
                output_data.append(building_row)

                # End of for row_data in range(len(groupby_list)):
        
            # End of if groupby_list is not None:
        else:   

            output_data = result_data


    # Build the headers based on the command line arguments in result_header.order
    for ele in result_header.order:
        
        if ele[0] == 'count':

            ele_val = count_title
            output_header.append(ele_val.lower())
        
        elif ele[0] == 'sum':

            ele_val = sum_title + ele[1][0]
            output_header.append(ele_val.lower())

        elif ele[0] == 'min':

            ele_val = min_title + ele[1][0]
            output_header.append(ele_val.lower())

        elif ele[0] == 'max':

            ele_val = max_title + ele[1][0]
            output_header.append(ele_val.lower())
            
        elif ele[0] == 'mean':
            ele_val = mean_title + ele[1][0]
            output_header.append(ele_val.lower())

        elif ele[0] == 'top':

            if top_capped:

                ele_val = top_title + ele[1][1] + '_capped'

            else:

                ele_val = top_title + ele[1][1]
    
            output_header.append(ele_val.lower())
        
        # End of for ele in result_header.order:

    # Adding _OTHER row to data if group-by was capped
    if groupby_capped:
        
        other_row = [] # List to hold the other row split

        other_row.append('_OTHER')

        for i in range(1, len(output_header)):

            other_row.append(None)

        output_data.insert(20, other_row)
    

    # Creating a writer object
    writting = csv.writer(sys.stdout)

    # Write the column headers
    writting.writerow(output_header)

    # Write the column rows
    writting.writerows(output_data)

class Organizer(argparse.Action):
    """
    A classed used to organized the command line arguments by the order
    they were passed in.

    """

    def __call__(self, parser, namespace, values, option_string = None):

        # Check if order is in namespace from argparse
        if not 'order' in namespace:

            # If not create a list in namespace called order
            setattr(namespace, 'order', [])

        # Set previous to namespace.order
        previous = namespace.order

        # Append a list of values and argparse action
        previous.append([self.dest, values])

        # Set order to previous in namespace
        setattr(namespace, 'order', previous)


class DataBlock:
    """ 
    A class used to represent Data

    ...

    Attributes
    ----------
    column_header : list
        A list containing the title of each column
    
    column_data : list
        A list containing the data of each row

    input : str
        The name of the file that is input

    top_capped : boolean
        A boolean to hold top's result has been capped

    groupby_capped : boolean
        A boolean to hold group-by result has been capped

    Methods
    -------
    add_header(self, new_header)
        Adds data to column_header

    add_data(self, new_data)
        Adds data to column_data

    column_sum(self, column_name, groupby_values = None, groupby_index = -1)
        Sums data of column

    column_min(self, column_name, groupby_values = None, groupby_index = -1)
        Gets the minimum value of a column

    column_max(self, column_name, groupby_values = None, groupby_index =-1)
        Gets the maximum value of a column

    column_mean(self, column_name, groupby_values = None, groupby_index = -1)
        Gets the mean(average) value of a column

    column_count(self, groupby_values = None, groupby_index = -1)
        Counts the records

    column_group(self, arguments, groupby_arg)
        Groups data by a field

    column_top(self, n, column_name)
        Gets the top n values of a field

    """


    def __init__(self, input_file):
        """
        Parameters
        ----------
        input_file : str
            The name of the input file

        """
    
        self.column_header = []
        self.column_data = []
        self.input = input_file
        self.top_capped = False
        self.groupby_capped = False
    
    def add_header(self, new_header):
        """
        Fills the column header list with the data passed.

        Parameters
        ----------
        new_header : str
            The title of each column header

        """

        # Setting the strings from new_header to be lower case before adding them to column_header
        self.column_header.extend(x.lower() for x in new_header)

    def add_data(self, new_data):
        """
        Fills the column data list with the data passed.

        Parameters
        ----------
        new_data : str
            The data of each row

        """

        self.column_data.append(new_data)


    def column_sum(self, column_name, groupby_values = None, groupby_index = -1):
        """
        Sums up the values of a column.

        If the arguments 'groupby_values' and 'groupby_index' are passed in, then sum
        will sum values based on the strings in groupby_values.

        Parameters
        ----------
        column_name : str
            The name of the column to be summed

        groupby_values : list, optional
            A list containing the names of interest (default is None)

        groupby_index : int, optional
            The location in the column_data of the names of interest (default is -1)

        Exceptions
        ----------
        ValueError
            If column passed contains values that can not be converted from string to float
            the message: 'Error: <input file>:<line number>: can't compute <column_name> on non-numeric value '<value>'' 
            will print.

            If more than 100 of these errors are found in a single column then 
            the message: 'Error: <input>:more than 100 non-numeric values found in aggreate column '<column_name>''
            will print and the program will extit.

        """

        # Variables
        non_numeric = 0 # Integer for tracking non-numeric values found

        # Checking if function should run in group-by mode
        if groupby_values != None and groupby_index != -1:

            # Variables
            sumval_list = [] # List holding the summed values

            # Finding the index location of the column_name parameter
            column_index = self.column_header.index(column_name.lower())

            for i in range(len(groupby_values)):

                # Reset tota_summed each iteration
                total_summed = 0.0

                for j in range(len(self.column_data)):

                    # Try to convert the value at column_index from a string to a float
                    try:

                        data_value = float(self.column_data[j][column_index])

                    except ValueError:

                        # Convert failed, print on standard error
                        print('Error: ' + self.input + ':' + str(j+1) + ': can\'t compute ' + column_name + ' on non-numeric value \'' + self.column_data[j][column_index] + '\'', file = sys.stderr)
                        non_numeric += 1

                        if non_numeric > 100:

                            # Print on standard error
                            print('Error: ' + self.input + ':more than 100 non-numeric values found in aggregate column \'' + column_name + '\'', file = sys.stderr)
                            exit(7)
                        
                        continue


                    # Checking if groupby_index string is equal to groupby_values string
                    if self.column_data[j][groupby_index] == groupby_values[i]:
                        total_summed = total_summed + float(data_value)

                    # End of for j in range(len(self.column_data))

                # Convert total_summed to a string before appending
                sumval_list.append(str(total_summed))

                # End of for i in range(len(groupby_values))
            
            return sumval_list

            # End of if groupby_values != None and groupby_index != -1:
        else:

            # Variables
            total_summed = 0.0 # Total summed value of entire column as a floating point

            # Finding the index location of the column_name parameter
            column_index = self.column_header.index(column_name.lower())

            for i in range(len(self.column_data)):
                
                # Try to convert the value at column_index from a string to a float
                try:

                    data_value = float(self.column_data[i][column_index])

                except ValueError:

                    # Convert failed, print on standard error
                    print('Error: ' + self.input + ':' + str(i+1) + ': can\'t compute ' + column_name + ' on non-numeric value \'' + self.column_data[i][column_index] + '\'', file = sys.stderr)
                    non_numeric += 1

                    if non_numeric > 100:

                        # Print on standard error
                        print('Error: ' + self.input + ':more than 100 non-numeric values found in aggregate column \'' + column_name + '\'', file = sys.stderr)
                        exit(7)
                        
                    continue

                total_summed = total_summed + data_value

                # End of for i in range(len(self.column_data)):

            return float(total_summed)


    def column_min(self, column_name, groupby_values = None, groupby_index = -1):
        """
        Finds the minimum value of a column.

        If the arguments 'groupby_values' and 'groupby_index' are passed in, then column_min
        will find the minimum value of each string in groupby_values.

        Parameters
        ----------
        column_name : str
            The name of the column to be summed

        groupby_values : list, optional
            A list containing the names of interest (default is None)

        groupby_index : int, optional
            The location in the column_data of the names of interest (default is -1)

        Exceptions
        ----------
        ValueError
            If column passed contains values that can not be converted from string to float
            the message 'Error: <input file>:<line number>: can't compute <column_name> on non-numeric value '<value>'' 
            will print.

            If more than 100 of these errors are found in a single column then 
            the message: 'Error: <input>:more than 100 non-numeric values found in aggreate column '<column_name>''
            will print and the program will extit.

        """

        # Variables
        non_numeric = 0 # Integer for tracking non-numeric values found

        # Finding the index location of the column_name parameter
        column_index = self.column_header.index(column_name.lower())

        # Checking if function should run in groupby mode or not
        if groupby_values != None and groupby_index != -1:

            # Variables
            minval_list = [] # List holding the minimum values

            # Initalizing temp_min to the max value of column_name
            temp_min = self.column_max(column_name.lower())

            for ele in groupby_values:

                # Reset min_val each iteration
                min_val = temp_min

                for j in range(len(self.column_data)):

                    # Checking if groupby_index string is equal to ele value
                    if self.column_data[j][groupby_index] == ele:

                        # Try to convert the value at column_index from a string to a float
                        try:

                            data_value = float(self.column_data[j][column_index])

                        except ValueError:

                            # Convert failed, print on standard error
                            print('Error: ' + self.input + ':' + str(j+1) + ': can\'t compute ' + column_name + ' on non-numeric value \'' + self.column_data[j][column_index] + '\'', file = sys.stderr)
                            non_numeric += 1

                            if non_numeric > 100:

                                # Print on standard error
                                print('Error: ' + self.input + ':more than 100 non-numeric values found in aggregate column \'' + column_name + '\'', file = sys.stderr)
                                exit(7)
                        
                            continue

                        if data_value < min_val:
                            min_val = data_value

                        # End of if self.column_data[j][groupby_index] == ele:

                    # End of for j in range(len(self.column_data)):

                # Convert min_val to a string before appending
                minval_list.append(str(min_val))

                # End of for ele in groupby_values:
            
            return minval_list

            # End of if groupby_values != None and groupby_index != -1:
        else:

            for i in range(len(self.column_data)):

                try:

                    # Setting the min_val to first value in column_data
                    min_val = float(self.column_data[i][column_index])
                    break

                except ValueError:

                    # Convert failed, print on standard error
                    print('Error: ' + self.input + ':' + str(i+1) + ': can\'t compute ' + column_name + ' on non-numeric value \'' + self.column_data[i][column_index] + '\'', file = sys.stderr)
                    non_numeric += 1

                    if non_numeric > 100:

                        # Print on standard error
                        print('Error: ' + self.input + ':more than 100 non-numeric values found in aggregate column \'' + column_name + '\'', file = sys.stderr)
                        exit(7)
                        
                    continue

            for i in range(1,len(self.column_data)):

                # Try to convert the column_data from a string to float
                try:

                    data_value = float(self.column_data[i][column_index])

                except ValueError:

                    # Convert failed, print on standard error
                    print('Error: ' + self.input + ':' + str(i+1) + ': can\'t compute ' + column_name + ' on non-numeric value \'' + self.column_data[i][column_index] + '\'', file = sys.stderr)
                    non_numeric += 1

                    if non_numeric > 100:

                        # Print on standard error
                        print('Error: ' + self.input + ':more than 100 non-numeric values found in aggregate column \'' + column_name + '\'', file = sys.stderr)
                        exit(7)
                        
                    continue


                if data_value < min_val:
                    min_val = data_value

                # End of for i in range(1,len(self.column_data)):
            
            return float(min_val) 

    
    def column_max(self, column_name, groupby_values = None, groupby_index =-1):
        """
        Finds the maximum value of a column.

        If the arguments 'groupby_values' and 'groupby_index' are passed in, then column_max
        will find the maximum value of each string in groupby_values.

        Parameters
        ----------
        column_name : str
            The name of the column to be summed

        groupby_values : list, optional
            A list containing the names of interest (default is None)

        groupby_index : int, optional
            The location in the column_data of the names of interest (default is -1)

        Exceptions
        ----------
        ValueError
            If column passed contains values that can not be converted from string to float
            the message 'Error: <input file>:<line number>: can't compute <column_name> on non-numeric value '<value>'' 
            will print.

            If more than 100 of these errors are found in a single column then 
            the message: 'Error: <input>:more than 100 non-numeric values found in aggreate column '<column_name>''
            will print and the program will extit.

        """

        # Variavles
        non_numeric = 0 # Integer for tracking non-numeric values found

        # Finding the index location of the column_name parameter
        column_index = self.column_header.index(column_name.lower())

        
        # Checking if function should run in groupby mode or not
        if groupby_values != None and groupby_index != -1:

            # Variables
            maxval_list = [] # List holding all the maximum values

            # Finding the minimum value in the column
            temp_max = self.column_min(column_name)

            for i in range(len(groupby_values)):

                # Reset max_val each iteration
                max_val = temp_max

                for j in range(len(self.column_data)):

                    # Try to convert the value at column_index from a string to a float
                    try:
                        data_value = float(self.column_data[j][column_index])

                    except ValueError:

                        # Convert failed, print on standard error
                        print('Error: ' + self.input + ':' + str(j+1) + ': can\'t compute ' + column_name + ' on non-numeric value \'' + self.column_data[j][column_index] + '\'', file = sys.stderr)
                        non_numeric += 1

                        if non_numeric > 100:

                            # Print on standard error
                            print('Error: ' + self.input + ':more than 100 non-numeric values found in aggregate column \'' + column_name + '\'', file = sys.stderr)
                            exit(7)
                        
                        continue

                    # Checking if groupby_index string is equal to groupby_values string
                    if self.column_data[j][groupby_index] == groupby_values[i]:
                        if data_value > max_val:
                            max_val = data_value

                    # End of for j in range(len(self.column_data)):

                # Convert max_val to string before appending
                maxval_list.append(str(max_val))

                # End of for i in range(len(groupby_values)):

            return maxval_list

            # End of if groupby_values != None and groupby_index != -1:
        else:
            
            for i in range(len(self.column_data)):
                try:

                    # Setting max_val to first value in column_data
                    max_val = float(self.column_data[i][column_index])
                    break

                except ValueError:

                    # Convert failed, print on standard error
                    print('Error: ' + self.input + ':' + str(i+1) + ': can\'t compute ' + column_name + ' on non-numeric value \'' + self.column_data[i][column_index] + '\'', file = sys.stderr)
                    non_numeric += 1

                    if non_numeric > 100:

                        # Print on standard error
                        print('Error: ' + self.input + ':more than 100 non-numeric values found in aggregate column \'' + column_name + '\'', file = sys.stderr)
                        exit(7)
                        
                    continue
                

            for i in range(len(self.column_data)):

                # Try to convert the column_data from string to a float
                try:

                    data_value = float(self.column_data[i][column_index])

                except ValueError:

                    # Convert failed, print on standard error
                    print('Error: ' + self.input + ':' + str(i+1) + ': can\'t compute ' + column_name + ' on non-numeric value \'' + self.column_data[i][column_index] + '\'', file = sys.stderr)
                    non_numeric += 1

                    if non_numeric > 100:

                        # Print on standard error
                        print('Error: ' + self.input + ':more than 100 non-numeric values found in aggregate column \'' + column_name + '\'', file = sys.stderr)
                        exit(7)
                        
                    continue

                if data_value > max_val:
                    max_val = data_value

                # End of for i in range(len(self.column_data)):
            
            return float(max_val)

    
    def column_mean(self, column_name, groupby_values = None, groupby_index = -1):
        """
        Finds the mean(average) value of a column.

        If the arguments 'groupby_values' and 'groupby_index' are passed in, then column_mean
        will find the mean value of each string in groupby_values.

        Parameters
        ----------
        column_name : str
            The name of the column to be summed

        groupby_values : list, optional
            A list containing the names of interest (default is None)

        groupby_index : int, optional
            The location in the column_data of the names of interest (default is -1)

        Exceptions
        ----------
        ValueError
            If column passed contains values that can not be converted from string to float
            the message 'Error: <input file>:<line number>: can't compute <column_name> on non-numeric value '<value>'' 
            will print.

            If more than 100 of these errors are found in a single column then 
            the message: 'Error: <input>:more than 100 non-numeric values found in aggreate column '<column_name>''
            will print and the program will extit.

        """

        # Variables
        non_numeric = 0 # Integer for tracking non-numeric values found

        # Checking if function should run in groupby mode or not
        if groupby_values != None and groupby_index != -1:

            # Variables
            meanval_list = [] # List of mean(average) values

            # Finding the index location of the column_name parameter
            column_index = self.column_header.index(column_name.lower())

            # Find the matching data of groupby_name location
            for i in range(len(groupby_values)):

                # Reseting variables each iteration
                total_summed = 0.0 # Float containing the summed total
                mean_val = 0.0  # Float containing the mean(average)
                total_items = 0 # Integer of the total items that were summed

                for j in range(len(self.column_data)):

                    # Check if string at groupby_index is not equal to groupby_values string
                    if self.column_data[j][groupby_index] != groupby_values[i]:
                        continue

                    # Try to convert the value at column_index from a string to a float
                    try:

                        data_value = float(self.column_data[j][column_index])

                    except ValueError:

                        # Convert failed, print to standard error
                        print('Error: ' + self.input + ':' + str(j+1) + ': can\'t compute ' + column_name + ' on non-numeric value \'' + self.column_data[j][column_index] + '\'', file = sys.stderr)
                        non_numeric += 1

                        if non_numeric > 100:

                            # Print to standard error
                            print('Error: ' + self.input + ':more than 100 non-numeric values found in aggregate column \'' + column_name + '\'', file = sys.stderr)
                            exit(7)
                        
                        continue

                    total_summed = total_summed + float(data_value)
                    total_items += 1

                    # End of for j in range(len(self.column_data)):

                if total_items == 0.0:
                    total_items = 1.0
                    
                # Convert the quotient to a float
                mean_val = float(total_summed/total_items)

                # Convert mean_val to a string before appending
                meanval_list.append(str(mean_val))

                # End of for i in range(len(groupby_values)):
            
            return meanval_list

            # End of if groupby_values != None and groupby_index != -1:
        else: 
            
            total_sum = self.column_sum(column_name)

            # Get the number of total items
            total_items = float(len(self.column_data))
            
            # Divide total_sum by total_items and return the quotient as a float
            return float(total_sum/total_items)


    def column_count(self, groupby_values = None, groupby_index = -1):
        """
        Finds the number of records.

        If the arguments 'groupby_values' and 'groupby_index' are passed in, then column_count
        will find the number of records of each string in groupby_values.

        Parameters
        ----------
        groupby_values : list, optional
            A list containing the names of interest (default is None)

        groupby_index : int, optional
            The location in the column_data of the names of interest (default is -1)

        """

        # Checking if function should run in groupby mode or not
        if groupby_values != None and groupby_index != -1:

            # Variables
            countval_list = [] # List containing the counted values
            
            for ele in groupby_values:

                # Reset totalgroup_records each iteration
                totalgroup_records = 0

                for j in range(len(self.column_data)):
                    
                    # Checking if groupby_index string is equal to ele value
                    if self.column_data[j][groupby_index] == ele:
                        totalgroup_records += 1

                    # End of for j in range(len(self.column_data)):

                # Convert totalgroup_records to string before appending
                countval_list.append(str(totalgroup_records))

                # End of for ele in groupby_values:
            
            return countval_list

            # End of if groupby_values != None and groupby_index != -1:
        else:
            
            # Variables
            total_records = 0 # Integer holding total number of records

            total_records = len(self.column_data)

            return total_records


    def column_group(self, arguments, groupby_arg):
        """
        Finds the data related to the field of interest and based on the arguments passed.

        Parameters
        ----------
        arguments : list
            A list with all the arguments passed at command line

        groupby_arg : str
            The field the data is going to be organized by

        Exceptions
        ----------
        ValueError
            If a column passed contains values that can not be converted from string to float
            the message 'Error: <input file>:<line number>: can't compute <column_name> on non-numeric value '<value>'' 
            will print.

            If more than 100 of these errors are found in a single column then 
            the message: 'Error: <input>:more than 100 non-numeric values found in aggreate column '<column_name>''
            will print and the program will extit.

        """
        
        # Variables
        groupby_field = groupby_arg # Setting groupby_field to the arugment passed to groupby
        temp_values = [] # List to hold all the values from column of interest
        results_list = [] # List for results
        argval_list = [] # List for all the argument calls

        # Finding the index location of the groupby_name parameter
        groupby_index = self.column_header.index(groupby_field.lower())

        # Fill temp_values with values from column of interest
        for i in range(len(self.column_data)):
            temp_values.append(self.column_data[i][groupby_index])
        
        # Creating a set of unique values
        cardinality_check = set(temp_values)
        if len(cardinality_check) > 20:

            # Checking if cardinality is too high
            if len(cardinality_check) >= 100:

                # Print on standard error
                print('Error: ' + self.input + ': The field ' + groupby_field + ' has to many unique values.', file = sys.stderr)

                exit(6)

            # Print to standard error
            print('Error:' + self.input + ': ' + groupby_arg + ' has been capped at 20 distinct values', file = sys.stderr)

            self.groupby_capped = True
            
        # Creating a set of distinct values
        groupby_values = [x for x in set(temp_values)]

        # Sort in ascending order
        groupby_values.sort()

        # Call the respective function based on elements in arguments.order
        for ele in arguments.order:

            if ele[0] == 'max':
                ele_list = self.column_max(ele[1][0], groupby_values, groupby_index)

            elif ele[0] == 'count':
                ele_list = self.column_count(groupby_values, groupby_index)

            elif ele[0] == 'sum':
                ele_list = self.column_sum(ele[1][0], groupby_values, groupby_index)

            elif ele[0] == 'min':
                ele_list = self.column_min(ele[1][0], groupby_values, groupby_index)

            elif ele[0] == 'max':
                ele_list = self.column_max(ele[1][0], groupby_values, groupby_index)
                
            elif ele[0] == 'mean':
                ele_list = self.column_mean(ele[1][0], groupby_values, groupby_index)

            elif ele[0] == 'top':
                ele_list = self.column_top(ele[1][0], ele[1][1], groupby_values, groupby_index)

            # Creating a 2D list
            argval_list.append(ele_list)

            # End of for ele in arguments.order:
        
        return argval_list


    def column_top(self, n, column_name, groupby_values = None, groupby_index = -1):
        """
        Finds the top n values in descending order

        Parameters
        ----------
        column_name : str
            The name of the column of interest

        n : int
            The number of items to retrieve

        groupby_values : list, optional
            A list containing the names of interest (default is None)

        groupby_index : int, optional
            The location in the column_data of the names of interest (default is -1)

        Restrictions
        ------------
        column_top is capped at 20 unique values.
        
        If the column of interest has more than 20 unique values then the error message:
        'Error: <input>: <column_name> has been capped at 20 distinct values' will print
        and the output result will only contain 20 items.
        
        """

        # Variables
        top_list = [] # Holds all the data from the column of interest
        formatter_list = [] # Formatter list to help format output data
        distinct_values = [] # Distinct values list to hold final formatted data
        format_place = ''
        k_val = int(n)

        # Checking if n passed is zero or negative
        if k_val <= 0:

            # Print on standard error
            print('Error: ' + self.input + ' top k can only take values greater than 0.', file = sys.stderr)

            exit(6)

        # Finding the index location of the column_name parameter
        column_index = self.column_header.index(column_name.lower())

        # Building top_list based on column_name
        for i in range(len(self.column_data)):

            top_list.append(self.column_data[i][column_index])

            # End of for i in range(len(self.column_data)):

        
        cardinality_check = set(top_list)

        # Checking if the cardinality is greater than 20
        if len(cardinality_check) > 20 and k_val > 20:

            k_val = 20
            
            # Print to standard error
            print('Error:' + self.input + ': ' + column_name + ' has been capped at 20 distinct values', file = sys.stderr)

            self.top_capped = True
                
        # Checking if top should run in group-by mode
        if groupby_values != None and groupby_index != -1:
            
            group_list = [] # List for holding all the output formatted values in order of group-by elements

            for element in groupby_values:

                # Variables that need to be reset for each element
                format_place = '' # String for formatting the values found for each element in groupby_values
                group_top = [] # List fro holding all the values in the field name passed with top
                
                for i in range(len(self.column_data)):
                    
                    # Checking if the string at groupby_index is not equal to element string
                    if self.column_data[i][groupby_index] != element:

                        continue

                    else:

                        group_top.append(self.column_data[i][column_index])

                # Create a list of the unique elements
                formatter_list = [[x, top_list.count(x)] for x in set(group_top)]

                # Storing by descending order
                formatter_list.sort(key= lambda x: x[1], reverse=True)

                # Checking if the list of unique values is less than the k passed
                if len(formatter_list) < k_val:

                    # Formatting and building a the ouput based on the length of the formatter list
                    for i in range(len(formatter_list)):

                        # Check weither or not to add a comma
                        if i == len(formatter_list) - 1:

                            format_place += (str(formatter_list[i][0]) + ": " + str(formatter_list[i][1]))

                        else:
                        
                            format_place += (str(formatter_list[i][0]) + ": " + str(formatter_list[i][1]) + ',')


                        # End of for i in range(k_val):

                    group_list.append([format_place])
                else:

                    # Formatting and building the output list based on k 
                    for i in range(k_val):

                        # Check weither or not to add a comma
                        if i == k_val - 1:

                            format_place += (str(formatter_list[i][0]) + ": " + str(formatter_list[i][1]))

                        else:
                        
                            format_place += (str(formatter_list[i][0]) + ": " + str(formatter_list[i][1]) + ',')


                        # End of for i in range(k_val):

                    group_list.append([format_place])

            distinct_values = group_list

        else:

            # Create a list of the unique elements
            formatter_list = [[x, top_list.count(x)] for x in set(top_list)]

            # Storing by descending order
            formatter_list.sort(key= lambda x: x[1], reverse=True)

            for i in range(k_val):

                if i == k_val - 1:

                    format_place += (str(formatter_list[i][0]) + ": " + str(formatter_list[i][1]))

                else:
                    
                    format_place += (str(formatter_list[i][0]) + ": " + str(formatter_list[i][1]) + ',')


                # End of for i in range(k_val):

            # Append a list format_place to distince_values
            distinct_values.append([format_place])

        # Checking if results are capped
        if self.top_capped:

            return distinct_values[:20]

        else:

            return distinct_values


if __name__ == '__main__':
    
    # Run main function
    main()

    # End of if __name__ == '__main__':