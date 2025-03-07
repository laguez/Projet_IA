from pycsp3 import *

def line_form_contraints(contraints,form): 
    for r in range(len(form)): 
        contraints.append(AllDifferent(form[r]))

def column_form_contraints(contraints,form):
    for c in range(len(form)): 
        contraints.append(AllDifferent(form[:,c]))

def line_color_contraints(contraints,color): 
    for r in range(len(color)): 
        contraints.append(AllDifferent(color[r]))

def column_color_contraints(contraints,color):
    for c in range(len(color)): 
        contraints.append(AllDifferent(color[:,c]))

def cell_contraint_equal_clues_values(contraints,clues,form,color): 
    for r in range(len(clues)) : 
        for c in range(len(clues)): 
             if clues[r][c] != (0, 0):
                if clues[r][c][0] != 0:
                    contraints.append(form[r][c] == clues[r][c][0])
                if clues[r][c][1] != 0:
                    contraints.append(color[r][c] == clues[r][c][1])

def uniq_combination(contraints,form,color):
    for r1 in range(len(form)):
        for c1 in range(len(form)):
            for r2 in range(len(form)):
                for c2 in range(len(form)):
                    if r1 != r2 or c1 != c2:
                        contraints.append(
                            (form[r1][c1] != form[r2][c2]) | 
                            (color[r1][c1] != color[r2][c2])
                        )
                
def generate_matrix(length): 
    result = []
    for r in range(n): 
        row = [] 
        for c in range(n): 
            row.append((0,0)) 
        result.append(row) 
    return result


def solve_tapestry(clues: list[list[(int, int)]]) -> list[list[(int, int)]]:
    # Put your code here
    
    n = len(clues) 
    m = len(clues[0])

    if n != m : 
        return None
    
    forme = VarArray(size=[n,n], dom=range(1,n+1))
    couleur = VarArray(size=[n,n], dom=range(1,n+1))

    contraints = []

    def line_form_contraints(contraints,form): 
        for r in range(len(form)): 
            contraints.append(AllDifferent(form[r]))

    def column_form_contraints(contraints,form):
        for c in range(len(form)): 
            contraints.append(AllDifferent(form[:,c]))

    def line_color_contraints(contraints,color): 
        for r in range(len(color)): 
            contraints.append(AllDifferent(color[r]))

    def column_color_contraints(contraints,color):
        for c in range(len(color)): 
            contraints.append(AllDifferent(color[:,c]))

    def cell_contraint_equal_clues_values(contraints,clues,form,color): 
        for r in range(len(clues)) : 
            for c in range(len(clues)): 
                if clues[r][c] != (0, 0):
                    if clues[r][c][0] != 0:
                        contraints.append(form[r][c] == clues[r][c][0])
                    if clues[r][c][1] != 0:
                        contraints.append(color[r][c] == clues[r][c][1])

    def uniq_combination(contraints,form,color):
        for r1 in range(len(form)):
            for c1 in range(len(form)):
                for r2 in range(len(form)):
                    for c2 in range(len(form)):
                        if r1 != r2 or c1 != c2:
                            contraints.append(
                                (form[r1][c1] != form[r2][c2]) | 
                                (color[r1][c1] != color[r2][c2])
                            )
                    
    def generate_matrix(length): 
        result = []
        for r in range(n): 
            row = [] 
            for c in range(n): 
                row.append((0,0)) 
            result.append(row) 
        return result

    cell_contraint_equal_clues_values(contraints,clues,forme,couleur)

    line_form_contraints(contraints,forme) 
    column_form_contraints(contraints,forme) 

    line_color_contraints(contraints,couleur)
    column_color_contraints(contraints,couleur)

    uniq_combination(contraints, forme, couleur)

    satisfy(contraints)

    solve()

    if solution() : 

        result = generate_matrix(n)
        for row in range(n): 
            for column in range(n):
                result[row][column] = (value(forme[row][column]), value(couleur[row][column]))
        return result
        
    else: 
        return None

def verify_format(solution: list[list[(int, int)]], n: int):
    validity = True
    if (len(solution) != n):
        validity = False
        print("The number of rows in the solution is not equal to n")
    for i in range(len(solution)):
        if len(solution[i]) != n:
            validity = False
            print(f"Row {i} does not contain the right number of cells\n")
        for j in range(len(solution[i])):
            if (not isinstance(solution[i][j], tuple)):
                validity = False
                print(f"Cell in row {i} and column {j} is not a tuple\n")
            elif len(solution[i][j]) != 2:
                validity = False
                print(f"Cell in row {i} and column {j} does not contain the right number of values\n")
    return validity

def parse_instance(input_file: str) -> list[list[(int, int)]]:
    with open(input_file) as input:
        lines = input.readlines()
    n = int(lines[0].strip())
    clues = [[(0, 0) for i in range(n)] for j in range(n)]
    for line in lines[1:]:
        i, j, s, c = line.strip().split(" ")
        clues[int(i)][int(j)] = (int(s), int(c))
    print(clues)
    return n, clues

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 tapestry.py instance_path")
        sys.exit(1)

    n, clues = parse_instance(sys.argv[1])
    
    solution = solve_tapestry(clues)
    if solution is not None:
        if (verify_format(solution, n)):
            print("Solution format is valid")
        else:
            print("Solution format is invalid")
    else:
        print("No solution found")

