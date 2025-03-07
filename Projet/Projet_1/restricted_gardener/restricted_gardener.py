from pycsp3 import *


def line_uniq_hedge(constraints, garden):
    constraints.append(AllDifferent(garden))


def visible_hedge(garden):
    n = len(garden)
    
    is_visible = VarArray(size=n, dom={0, 1})
    
    if n > 0:
        satisfy(is_visible[0] == 1)
    
    for i in range(1, n):
        max_previous = Maximum(garden[j] for j in range(i))
        satisfy(If(garden[i] > max_previous, Then=is_visible[i] == 1, Else=is_visible[i] == 0))
    
    return Sum(is_visible)


def solve_restricted_gardener(instruction: int, n: int):

    if not isinstance(instruction, int) or instruction > n or instruction < 1:
        return None

    constraints = []

    garden = VarArray(size=n, dom=range(1, n+1))  

    
    line_uniq_hedge(constraints, garden)
    
    number_visible_hedge = Var(dom=range(1, n+1))  

    constraints.append(number_visible_hedge == visible_hedge(garden))
    constraints.append( instruction == number_visible_hedge)

    satisfy(constraints)

    solve()

    if solution():
        result = [] 
        for hedge in range(n) : 
            result.append(value(garden[hedge]))
        return result
    return None
    

def verify_format(solution: list[int], n: int):
    if len(solution) != n:
        print(f"The solution does not contain the right number of cells\n")
        for i in range(len(solution)):
            if (not isinstance(solution[i], int)):
                print(f"Cell at index {i} is not an integer\n")

    print(solution)
    return True


def parse_instance(input_file: str) -> tuple[int, int]:
    with open(input_file, "r") as file:
        lines = file.readlines()
    n = int(lines[0].strip())
    instruction = int(lines[1].strip())

    return instruction, n


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 restricted_gardener.py instance_path")
        sys.exit(1)

    instruction, n  = parse_instance(sys.argv[1])


    solution = solve_restricted_gardener(instruction, n)
    if solution is not None:
        if (verify_format(solution, n)):
            print("Solution format is valid")
        else:
            print("Solution is invalid")
    else:
        print("No solution found")
