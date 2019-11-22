'''
Amazon order text parser.

1) Copy Amazon order table <body> as HTML, paste to TextEdit, save to Desktop as "day-of-week".

2) Change variable TEXT_FILE_OF_CURRENT_ORDERS to current filename from step 1.

3) Run program and view TODAYS_ORDERS.txt on Desktop to see all current unshipped items sorted alphanumerically.

NOTE:

* ORDER_IDs.txt contains the unshipped Order Id's; it is written to the Desktop. Only NEW Order Id's will be appended to the text file each time the program is run. DO NOT alter or delete ORDER_IDs.txt, only delete this file after all orders have been processed.

* TODAYS_ORDERS.txt contains the current sorted orders needed to be processed. This text file is created / overwritten each time the program is run. Do not delete this file.
'''
import os

TEXT_FILE_OF_CURRENT_ORDERS = 'sun_78.rtf'

'''Check if ORDER_IDs.txt file exists on hard drive. If not, initialize an empty list that will contain the current unshipped Order ID's. If so, populate a list with the current unshipped Order ID's contained in the text file.'''
if not os.path.isfile('ORDER_IDs.txt'):
    order_id_list = []
else:
    with open('ORDER_IDs.txt', 'r') as f:
        order_id_STRING = f.read()                    # returns a string
        order_id_list = order_id_STRING.split(',')    # returns a list of parsed strings

def find_all(a_str, sub):
    """Find a substring in a text file and return its index.

    a_str : the text file
    sub : the substring
    rtype : int
    """
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)

def create_current_orders_dictionary():
    """Parse an unshipped orders text file, populate a dictionary with current orders and return the dictionary.

    Dictionary key : An Order ID
    Dictionary value : List of SKU's for that Order ID

    rtype : Dictionary
    """
    with open(TEXT_FILE_OF_CURRENT_ORDERS, 'r') as f:
        AMZN = f.read()                    # returns a string

        substring = "a href=\"/orders-v3/order/"  # ORDER ID
        substring2 = "SKU</span>:"                # SKU

        list_of_start_indices_for_order_id = list(find_all(AMZN, substring))
        # There are 4 instances of the substring, I want to populate the list of start
        # indices with only the first occurance of each, so I reset the variable to
        # contain a list of each fourth element
        list_of_start_indices_for_order_id = list_of_start_indices_for_order_id[::4]
        list_of_start_indices_for_sku = list(find_all(AMZN, substring2))

        ORDER_DICT = {}   # { ORDER-ID : [ SKU'S ] }

        j = 0
        for i in range(len(list_of_start_indices_for_order_id) - 1):
            while j <= len(list_of_start_indices_for_sku):
                try:
                    current_num = list_of_start_indices_for_order_id[i]
                    next_num = list_of_start_indices_for_order_id[i + 1]

                    order = AMZN[list_of_start_indices_for_order_id[i] + 25 : list_of_start_indices_for_order_id[i] + 60].split('>')[0][:-1]

                    # unknown bug: some order variables were not set to the correct order string,
                    # quick fix: check if the length is greater than 19 (a valid order
                    # id length), if so set the order variable to the correct order id by
                    # splitting the string at the '/' (the wrong order string contains '/')
                    if len(order) > 19:
                        order = order.split('/')[0]

                    # APPEND NEW ORDER ID TO ORDER-ID TEXT FILE
                    if order not in order_id_list:
                        with open('ORDER_IDs.txt', 'a') as f:
                            f.write(order + ',')
                        order_id_list.append(order)

                        sku_list = []
                        while list_of_start_indices_for_sku[j] < next_num:
                            sku = AMZN[list_of_start_indices_for_sku[j] + 13 : list_of_start_indices_for_sku[j] + 60].split('<')[0]
                            sku_list.append(sku)
                            j += 1

                        ORDER_DICT[order] = sku_list
                except Exception as e:
                    print(e)
                    continue
                break

        # THE FIRST FOR LOOP BREAKS BEFORE LAST ORDER, THE CODE BELOW EXTRACTS THE LAST ORDER AND APPENDS TO THE ORDER DICTIONARY JUST LIKE ALL PREVIOUS ORDERS
        last_order_index = list_of_start_indices_for_order_id[-1]
        order = AMZN[last_order_index + 25 : last_order_index + 60].split('>')[0][:-1]

        if len(order) > 19:
            order = order.split('/')[0]

        if order not in order_id_list:
            with open('ORDER_IDs.txt', 'a') as f:
                f.write(order + ',')
            order_id_list.append(order)

            sku_list = []

            for last_sku_index in list_of_start_indices_for_sku:

                if last_sku_index > last_order_index:
                    last_order_sku = AMZN[last_sku_index + 16 : last_sku_index + 60].split('<')[0]
                    sku_list.append(last_order_sku)

            ORDER_DICT[order] = sku_list

        return ORDER_DICT

def verify_order_count():
    """Parse a text file containing the current Order ID's and print the number of Order ID's it contains.

    If the current unshipped orders quanitiy equals the amount of Order ID's in the text file all orders were parsed successfully.
    """
    if os.path.isfile('ORDER_IDs.txt'):
        with open('ORDER_IDs.txt', 'r') as f:
            order_id_STRING = f.read()                    # returns a string
            order_id_list = order_id_STRING.split(',')    # returns a list of parsed strings

            print('Total orders: ', len(order_id_list) - 1) # -1 because order list appends empty string at end

'''Initialize and populate a dictionary containing the current batch of unshipped orders. If order_id_list already contains a batch of unshipped orders from a previous day then this dictionary will only contain the current orders that have not been parsed yet.'''
current_orders_dict = create_current_orders_dictionary()

'''Initialize a list and populate it with all currently unshipped items; sort the list alphanumerically.'''
pulling_list = []
for order in current_orders_dict.values():
    for item in order:
        pulling_list.append(item)
pulling_list.sort()

'''Create text file and write all sorted unshipped items; this will serve as the list containing all current unshipped items, sorted alphanumerically, that need to be processed.'''
with open('TODAYS_ORDERS.txt', 'w') as f:
    for item in pulling_list:
        f.write(item + '\n')

'''Print total order quantity to verify all orders have been processed.'''
verify_order_count()
