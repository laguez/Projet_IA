from pycsp3 import *

def solve_gardener(dimension: int, instruction_list: list[list[int]]) -> list[list[int]] | None:
    instructions_count = len(instruction_list)
    garden = VarArray(size=(dimension, dimension), dom=range(1, dimension + 1))

    for row in garden:
        satisfy(AllDifferent(row))

    for column in zip(*garden):
        column = list(column)
        satisfy(AllDifferent(column))

    visible_hedges_count = count_matrix_visible_hedges(garden)

    for i in range(instructions_count):
        for j in range(dimension):
            if isinstance(instruction_list[i][j], int) and instruction_list[i][j] > 0:
                satisfy(visible_hedges_count[i][j] == instruction_list[i][j])

    solve()

    if solution():
        return [[value(garden[i][j]) for j in range(dimension)] for i in range(dimension)]

    return None

def count_array_visible_hedges(garden_line: list[int], var_array_name: str='') -> Sum:
    n = len(garden_line)

    visible_state = VarArray(size=n, dom={0, 1}, id=var_array_name)

    if n > 0:
        satisfy(visible_state[0] == 1)

    for i in range(1, n):
        max_previous = Maximum(garden_line[j] for j in range(i))
        satisfy(If(garden_line[i] > max_previous, Then=visible_state[i] == 1, Else=visible_state[i] == 0))

    return Sum(visible_state)

def count_matrix_visible_hedges(garden: list[list[int]]) -> list[list[int]]:
    n = len(garden)
    visible_counts = [[0] * n for _ in range(4)]

    for j in range(n):
        column = [garden[i][j] for i in range(n)]
        visible_counts[0][j] = count_array_visible_hedges(column, var_array_name=f'top{j}')
        visible_counts[3][j] = count_array_visible_hedges(column[::-1], var_array_name=f'bottom{j}')

    for i in range(n):
        row = garden[i]
        visible_counts[1][i] = count_array_visible_hedges(row, var_array_name=f'left{i}')
        visible_counts[2][i] = count_array_visible_hedges(row[::-1], var_array_name=f'right{i}')

    return visible_counts

def verify_format(solution: list[list[int]], n: int):
    validity = True
    if (len(solution) != n):
        validity = False
        print("The number of rows in the solution is not equal to n")
    for i in range(len(solution)):
        if len(solution[i]) != n:
            validity = False
            print(f"Row {i} does not contain the right number of cells\n")
        for j in range(len(solution[i])):
            if (not isinstance(solution[i][j], int)):
                validity = False
                print(f"Cell in row {i} and column {j} is not an integer\n")

    return validity

def parse_instance(input_file: str) -> tuple[int, list[list[int]]]:
    with open(input_file) as input:
        lines = input.readlines()

    n = int(lines[0].strip())
    instructions = []

    for line in lines[1:5]:
        instructions.append(list(map(int, line.strip().split(" "))))
        assert len(instructions[-1]) == n

    return n, instructions


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 gardener.py instance_path")
        sys.exit(1)

    n, instructions = parse_instance(sys.argv[1])
    solution = solve_gardener(n, instructions)

    if solution is not None:
        if verify_format(solution, len(instructions[0])):
            print("Solution format is valid")
        else:
            print("Solution format is invalid")
    else:
        print("No solution found")
