import db

print('\ndelete - Deletes all rows from table\nquit - quits the manager\ndisplay ["all"] - displays table based on parameter')

with db.Session() as session:
    while True:
        response = input('>>')
        if response == 'delete':
            session.delete_table()
            print('Table cleared')

        elif response == 'quit':
            break

        elif response == 'display all':
            table = session.get_table()
            s = ''
            if not table:
                s = 'NO TABLE TO DISPLAY'
            for row in table:
                print(row)

        else:
            print(session.raw(response))
            