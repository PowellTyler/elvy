import service
from getpass import getpass
import os
import sys
import re


def print_table(rows):
    """
    Given a list of association, password pair dicts print
    out a table
    """
    os.system('CLS')
    s = ('| ID   | ASSOCIATION             | PASSWORD \n'
         '+--------------------------------+-------------------------')
    for row in rows:
        association = row['association']
        if len(association) > 22:
            association = association[:19] + '...'
        s += '\n| {:4s} | {:23s} | {}'.format(row['id'], association, row['password'])
        s += '\n+--------------------------------+-------------------------'

    print(s)


def display_main_page():
    """
    Displays the main page with the valid options to choose from

    1 - Show/Edit passwords and associations
    q - Quits the program
    """
    while True:
        os.system('CLS')
        print('Please select an option\n\n1 - Show/Edit passwords and associations\nq - Quits the program\n\n')
        response = input('>>')
        if response == '1':
            display_table_edit_page()
        elif response == 'q':
            break


def display_table_edit_page():
    """
    Displays the table and the valid options for adding and deleting passwords
    from the table
    """
    while True:
        print_table(service.get_passwords(phrase))
        print('\n\n')
        print('1 - Add password')
        print('2 - Remove Password')
        print('3 - Go back')
        response = input('\n\n>>')

        if response == '1':
            display_table_create_message()

        elif response == '2':
            display_table_delete_message()
            
        elif response == '3':
            break 


def display_table_delete_message():
    """
    Displays the message for deleting passwords as well as takes in input
    to determine which rows to delete
    """
    print('Enter the IDs of the passwords you want to delete,\n'
        'you can delete multiple passwords by seperating IDs by commas\n'
        'or a range of values by enter two numbers seperated by a "-"\n\n')
    response = input('>>')
    match = re.search(r'(\d+)\s*-\s*(\d+)', response)
    if match:
        print('\nDeleting rows this may take some time')
        for id in range(int(match.group(1)), int(match.group(2)) + 1):
            service.delete_password(phrase, id)
    else:
        id_list = response.split(',')
        for id in id_list:
            try:
                int(id)
                service.delete_password(phrase, id)
            except Exception:
                pass


def display_table_create_message():
    """
    Displays the message for adding passwords as well as takes in input
    for creating a new row
    """
    password = input('Enter Password: ')
    association = input('Enter Association: ')
    print('\n\n')
    if len(password) > 0:
        service.add_password(phrase, password, association)

# Determines if user has provided a passphrase for the database yet and displays a message to create a new
# one if they have not yet.  Alternatively if one is already in the database then ask the user for it
if not service.is_passphrase_set():
    while True:
        phrase = getpass('Please enter a memorable passphrase\nPassphrase must be 16 characters long\n**ONCE A PASSPHRASE HAS BEEN SET IT CANNOT BE RESET**\n(Text will not display)\n\n>>')
        if len(phrase) == 16:
            print('Passphrase successfully set.')
            service.set_passphrase(phrase)
            break
else:
    while True:
        phrase = getpass('Please enter passphrase (Text will not display)\n\n>>')
        if service.validate_passphrase(phrase):
            print('Success!')
            break
display_main_page()
