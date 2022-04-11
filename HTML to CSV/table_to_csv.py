import os
import sys
import re 

def main():

    """
        table_to_csv takes in a valid HTML that contains tables with valid data and
        converts the data from HTML format to CSV format.

        The input file is taken from the system standard input and the output
        is printed to the system standard output.

    """

    # Variables
    table_list = [] # List for holding the sparated table lists
    raw_string = '' # String for holding all the data in one string
    raw_data = [] # List for holding the initial data
    built_output = [] # List for building the output data
    output_title = [] # List for holding each table title for output
    table_counter = 0 # Integer for adding to table title
    total_br = 0 # Integer for tracking the number of <br /> tags
    printed_titles = 0 # Integer for printing the titles 
    add_break = 0 # Integer for adding the newline

    input_data = sys.stdin.readlines()

    # Concatenate all the data into one string
    for line in input_data:

        raw_string = raw_string + line.strip()
    
    raw_data.append(raw_string)
    
    # Separating the raw data by the table tags
    for i in range(len(raw_data)):

        raw_element = raw_data[i]
        
        # Checking if <br /> tag is present
        br_matches = re.findall(r'<br.*?>',raw_element, re.IGNORECASE)
        if br_matches:
            total_br += len(br_matches)

        raw_element = re.sub(r'</table.*?>', 'END_TABLE_VARIABLE_cookie', raw_element, re.IGNORECASE)

        raw_element = re.sub(r'<table.*?>', '', raw_element)

        raw_element = re.sub(r'<br.*?>', '', raw_element)

        split_tables = filter(None, raw_element.split(r'END_TABLE_VARIABLE_cookie'))

    
    # Create a 2D list of each table tag    
    for element in split_tables:

        table_list.append([element])
    

    # Building the output data list
    for table in table_list:

        # Variables to reset for each table
        table_counter += 1 # Integer for the current table
        table_title = 'TABLE ' + str(table_counter) + ':' # String for each table title
        row_data = [] # List containing every row of the table
        extracted_data = [] # List for data extracted from each row
        total_cells = 0 # Integer for the maximum cell number of each table

        output_title.append(table_title)

        # Grabbing the table data string
        table_data = table[0]
        
        # Separating the row from the table string
        row = re.findall(r'<tr.*?>.*?</tr.*?>', table_data, re.IGNORECASE | re.DOTALL)

        row_data.extend(row)

        # Separating the data from <th> and <td> tags, and getting the number of cells of each row
        for row_element in range(len(row_data)):
            
            # Finding the number of cells for each row has
            matches = re.findall(r'<t[d|h].*?>.*?</t[d|h]>*?>', row_data[row_element], re.IGNORECASE)

            # Replacing all whitespace that is greater than one with one whitespace
            strip_data = re.sub(r' +', ' ', row_data[row_element])

            # Replacing all opening <t> tags with nothing
            strip_data = re.sub(r'<t[\w].*?>', '', strip_data)

            # Finding everyting located before a closing </td> or </tr> tag
            strip_data = re.findall(r'(.*?)\</t[d|h].*?>', strip_data, re.IGNORECASE)

            extracted_data.extend([strip_data])

            # Getting the largest number of cells of each row has per table
            if len(matches) > total_cells:

                total_cells = len(matches)

        # Stripping white spaces and adding comma's for CSV representation
        for element in extracted_data:

            for ele in range(len(element)):
                
                if ',' in element[ele]:
                    print('Error: Invalid input, comma can not be placed between matching <td></td> or matching <th></th> tags', file=sys.stderr)
                    exit(6)

                element[ele] = element[ele].strip()

                if ele < len(element) - 1:

                    element[ele] = element[ele] + ','

        # Ensuring every table contains atleast one row and column
        if total_cells == 0:

            total_cells = 1

        # Filling the smaller rows with comma's to match the desired column length
        for row_ele in extracted_data:
            
            row_size = len(row_ele)
            
            if row_size == 0:

                while row_size < total_cells - 1:

                    row_size += 1

                    row_ele.extend(',')

            else:

                while row_size < total_cells:

                    row_size += 1

                    row_ele.extend(',')


        built_output.append(extracted_data)
 

    # Grabing how many tables their are
    total_title = len(output_title)
    
    # Output the data
    for table in built_output:

        if printed_titles < total_title:

            print(output_title[printed_titles])

            printed_titles += 1
        
        for rows in table:

            for rows_data in range(len(rows)):

                print(rows[rows_data], end='')

            print('\n', end='')

        if add_break < total_br-1:

            print('\n', end='')

            add_break += 1
        

if __name__ == '__main__':
    main()