def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]
# creates all rows and column groupings for standard sudoku
rows = 'ABCDEFGHI'
cols = '123456789'
reverse_cols = cols[::-1]
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

#crates diagonal groupings 
diagonal_units_top = [[ row+cols[i] for i,row in enumerate(rows)] ]
diagonal_units_bottom = [[ row+reverse_cols[i] for i,row in enumerate(rows)] ]
# adds all the types of groupings to array
unitlist = row_units + column_units + square_units + diagonal_units_top + diagonal_units_bottom
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
# creates peers for every cell in sudoku
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)



def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)

def eliminate(values):
    '''
    elimantes values for all the peers of a solved cell
    '''
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

def only_choice(values):
    '''
    If a unique digit is found for a given cell in a given box
    the function changes the value of the cell to that unique value
    '''
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def reduce_diagonal_puzzle(values):
    
    stalled = False
    while not stalled:
        # keep track of all solved values
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # use to constraints to solve soudoku
        values = eliminate(values) #eliminate is a constraint that applies to all units, diagonal, box, row, etc...
        values = only_choice(values) # this constraint applies to just box unit
        # see if progress was made on solved values
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """Using depth-first search and propagation, try all possible values.
        a diagonal constraint will be added to check for solving diagonal sodoku 
    """
    # First, reduce the puzzle using the previous function
    values = reduce_diagonal_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt



############################# helpers above
assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    twins = { tuple(sorted([box,peer])):values[peer] 
                for box,peer_col in peers.items() 
                for peer in peer_col  if values[peer] == values[box] and len(values[peer] ) == 2 }
    # iterate through all twins
    for (key1,key2),val in twins.items():
        #find all the common peers for each twin
        common_peers = set(peers[key1]).intersection(set(peers[key2]))
        # remove any value from the twins neigboring peers 
        # that share the same value
        for peer in common_peers:
            val_list = list(val)
            twin_val1 = val_list[0]
            twin_val2 = val_list[1]
            val_str = values[peer]
            if twin_val1 in val_str:
                val_str = val_str.replace(twin_val1, "")
            if twin_val2 in val_str:
                val_str = val_str.replace(twin_val2, "")            
            values[peer] = val_str
    return values

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # convert str to testable hash_grid 
    values = grid_values(grid)
    # use depth-first search with constraint propagation to return solved sodoku
    return search(values)
if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
