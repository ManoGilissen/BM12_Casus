loop  = 1
while loop == 1:
    toDo = input('\nUit te voeren functie (type "?" voor een lijst met functies): ')
    if toDo == 'q' or toDo == 'quit':
        exitMsg = '\nDoei\n'
        loop = 0
    else:
        print('Executing ', toDo, '\n')
        eval(toDo)