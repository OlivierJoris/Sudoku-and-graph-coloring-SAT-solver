#!/usr/bin/python

import sys, os, glob, random
import subprocess

# reads a sudoku from file
# columns are separated by |, lines by newlines
# Example of a 4x4 sudoku:
# |1| | | |
# | | | |3|
# | | |2| |
# | |2| | |
# spaces and empty lines are ignored
def sudoku_read(filename):
    myfile = open(filename, 'r')
    sudoku = []
    N = 0
    for line in myfile:
        line = line.replace(" ", "")
        if line == "":
            continue
        line = line.split("|")
        if line[0] != '':
            exit("illegal input: every line should start with |\n")
        line = line[1:]
        if line.pop() != '\n':
            exit("illegal input\n")
        if N == 0:
            N = len(line)
            if N != 4 and N != 9 and N != 16:
                exit("illegal input: only size 16, 9, and are supported\n")
        elif N != len(line):
            exit("illegal input: number of columns not invariant\n")
        line = [int(x) if x >= '0' and x <= '9' else 0 for x in line]
        sudoku += [line]
    return sudoku

# print sudoku on stdout
def sudoku_print(myfile, sudoku):
    if sudoku == []:
        myfile.write("impossible sudoku\n")
    N = len(sudoku)
    for i in range(2 * N + 1):
        myfile.write("-")
    myfile.write("\n")
    for line in sudoku:
        myfile.write("|")
        for number in line:
            myfile.write(" " if number == 0 else str(number))
            myfile.write("|")
        myfile.write("\n")
        for i in range(2 * N + 1):
            myfile.write("-")
        myfile.write("\n")

# get number of constraints for sudoku
def sudoku_constraints_number(sudoku):
    N = len(sudoku)
    count = 4 * N * N * ( 1 + N * (N - 1) / 2)
    for line in sudoku:
        for number in line:
            if number > 0:
                count += 1
    return count

# prints the generic constraints for sudoku of size N
def sudoku_generic_constraints(myfile, N):

    def output(s):
        myfile.write(s)

    def newlit(i,j,k):
        output(str((N+1)**2 * i + (N+1) * j + k) + " ")

    def newneglit(i,j,k):
        output(str('-') + str((N+1)**2 * i + (N+1) * j + k) + " ")

    def newcl():
        output("0\n")

    def newcomment(s):
#        output("c %s\n"%s)
        output("")

    if N == 9:
        n = 3
    elif N == 4:
        n = 2
    elif N == 16:
        n = 4
    else:
        exit("Only supports size 16, 9, and 4")

    # Each cell of the sudoku must contains striclty one number in [1, N].
    for line in range(1, N + 1):
        for column in range(1, N + 1):
            propositions = []
            for number in range(1, N + 1):
                newlit(line, column, number)
                propositions.append([line, column, number])    
            newcl()
            for i in range(N + 1):
                for p in propositions[i + 1:]:
                    newneglit(propositions[i][0], propositions[i][1], propositions[i][2])
                    newneglit(p[0], p[1], p[2])
                    newcl()
    
    # Each line don't have two cells with the same number.
    for line in range(1, N + 1):
        for number in range(1, N + 1):
            propositions = []
            for column in range(1, N + 1):
                newlit(line, column, number)
                propositions.append([line, column, number]) 
            newcl()
            for i in range(N + 1):
                for p in propositions[i + 1:]:
                    newneglit(propositions[i][0], propositions[i][1], propositions[i][2])
                    newneglit(p[0], p[1], p[2])
                    newcl()

    # Each column don't have two cells with the same number.
    for column in range(1, N + 1):
        for number in range(1, N + 1):
            propositions = []
            for line in range(1, N + 1):
                newlit(line, column, number)
                propositions.append([line, column, number]) 
            newcl()
            for i in range(N + 1):
                for p in propositions[i + 1:]:
                    newneglit(propositions[i][0], propositions[i][1], propositions[i][2])
                    newneglit(p[0], p[1], p[2])
                    newcl()

    # Each square don't have two cells with the same number.
    for line_offset in range(1, N + 1, n):
        for column_offset in range(1, N + 1, n):
            for number in range(1, N + 1):
                propositions = []
                for line in range(n):
                    for column in range(n):
                        newlit(line + line_offset, column + column_offset, number)
                        propositions.append([line + line_offset, column + column_offset, number]) 
                newcl()
                for i in range(N + 1):
                    for p in propositions[i + 1:]:
                        newneglit(propositions[i][0], propositions[i][1], propositions[i][2])
                        newneglit(p[0], p[1], p[2])
                        newcl()

def sudoku_specific_constraints(myfile, sudoku):
    def output(s):
        myfile.write(s)

    def newlit(i,j,k):
        N = len(sudoku)
        output(str((N+1)**2 * i + (N+1) * j + k) + " ")

    def newcl():
        output("0\n")

    N = len(sudoku)
    for i in range(N):
        for j in range(N):
            if sudoku[i][j] > 0:
                newlit(i + 1, j + 1, sudoku[i][j])
                newcl()

def sudoku_solve(filename):
    command = "java -jar org.sat4j.core.jar sudoku.cnf"
    process = subprocess.Popen(command, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    for line in out.split(b'\n'):
        line = line.decode("utf-8")
        if line == "" or line[0] == 'c':
            continue
        if line[0] == 's':
            if line != 's SATISFIABLE':
                return []
            continue
        if line[0] == 'v':
            line = line[2:]
            units = line.split()
            if units.pop() != '0':
                exit("strange output from SAT solver:" + line + "\n")
            units = [int(x) for x in units if int(x) >= 0]
            N = len(units)
            if N == 16:
                N = 4
            elif N == 81:
                N = 9
            elif N == 256:
                N = 16
            else:
                exit("strange output from SAT solver:" + line + "\n")
            sudoku = [ [0 for i in range(N)] for j in range(N)]
            for number in units:
                sudoku[number // (N+1)**2 - 1][( number // (N+1) )% (N+1) - 1] = number % (N+1)
            return sudoku
        exit("strange output from SAT solver:" + line + "\n")
        return []

def print_loading_bar(current, total):
    """
    Prints a loading bar given the index of the current element treated and
    the total number of elements.
    Arguments:
    ----------
    - `current`: the current treated element.
        where 't' is the current time step.
    - `total`: the total number of elements to be treated.
    """
    scale = 50
    percent = ("{0:." + str(1) + "f}").format(100 * (float(current) / float(total)))
    filledSize = int(scale * current // total)
    bar = '█' * filledSize + '⣿' * (scale - filledSize)
    print(f'\r|{bar}| {percent}% {"completed."}', end = "\r")
    if current == total: 
        print('\n')

def make_sol_unsat(myfile):
    """
    Adds clauses to sudoku.cnf to make the actual solution found 
    unsatisfiable.
    Arguments:
    ----------
    - `myfile`: descriptor of the sudoku.cnf file.
    """
    command = "java -jar org.sat4j.core.jar sudoku.cnf"
    process = subprocess.Popen(command, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = process.communicate()
    # Add a disjunction making the model found not anymore a model.
    for line in out.split(b'\n'):
        line = line.decode("utf-8")
        if line == "" or line[0] == 'c':
            continue
        if line[0] == 's':
            if line != 's SATISFIABLE':
                return 
            continue
        if line[0] == 'v':
            line = line[2:]
            units = line.split()
            if units.pop() != '0':
                exit("strange output from SAT solver:" + line + "\n")
            units = [x for x in units]
            add_negation(myfile, units)
            return 
        exit("strange output from SAT solver:" + line + "\n")

def add_negation(myfile, clause):
    """
    Adds the negation of a clause to a given cnf file. 
    Arguments:
    ----------
    - `myfile`: descriptor of the cnf file.
    - `clause`: the clause that will be negated.
    """
    def output(s):
        myfile.write(s)

    def newlit(i):
        output(str(i) + " ")

    def newcl():
        output("0\n")

    for element in clause:
        if int(element) > 0:
            newlit('-' + str(int(element)))
        else:
            newlit(abs(int(element)))
    newcl()

def check_sat():
    """
    Checks if the sudoku.cnf is satisfiable.
    """
    command = "java -jar org.sat4j.core.jar sudoku.cnf"
    process = subprocess.Popen(command, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = process.communicate()
    for line in out.split(b'\n'):
        line = line.decode("utf-8")
        if line == "" or line[0] == 'c':
            continue
        if line[0] == 's':
            return (line == 's SATISFIABLE')

def update_cnf(sudoku, size):
    """
    Updates the sudoku.cnf file according to the representation of 
    sudoku.
    Arguments:
    ----------
    - `sudoku`: matrix representing the sudoku.
    - `size`: size of the sudoku.
    """
    myfile = open("sudoku.cnf", 'w')
    myfile.write("p cnf "+str(size)+str(size)+str(size)+" "+
                str(sudoku_constraints_number(sudoku))+"\n")
    sudoku_generic_constraints(myfile, size)

    sudoku_specific_constraints(myfile, sudoku)
    
    myfile.close()

def has_unique_sol():
    """
    Checks if the sudoku.cnf has a unique sol.
    Return:
    -------
    - True if it has a unique sol.
    - False otherwise.
    """
    if check_sat():
        myfile = open("sudoku.cnf", 'a')
        make_sol_unsat(myfile)
        myfile.close()
        if not check_sat():
            return True

    return False

def generate_sudoku(size):
    """
    Generates a sudoku of a given size and displays it on stdout.
    Arguments:
    ----------
    - `size`: size of the sudoku.
    """
    # Generates the first line randomly (size! possible different sudokus)
    numbers = []
    for i in range(size):
        numbers.append(i + 1)

    random.seed()
    random.shuffle(numbers)

    sudoku = [[0 for i in range(size)] for j in range(size)]
    for i in range(size):
        sudoku[0][i] = numbers[i]

    update_cnf(sudoku, size)
    sudoku = sudoku_solve("sudoku.cnf")

    prevValue = 0

    # Delete numbers from the solved sudoku and checks if it makes it have 
    # more than one solution.
    for i in range(size):
        for j in range(size):
            print_loading_bar((i + 1) * size + j + 1, (size * size) + size)
            prevValue = sudoku[i][j]
            sudoku[i][j] = 0
            update_cnf(sudoku, size)
            if not has_unique_sol():
                sudoku[i][j] = prevValue
                update_cnf(sudoku, size)

    sudoku_print(sys.stdout, sudoku)

def print_program_use():
    """
    Prints the program use to the standard output.
    """
    print("Program use :\n")
    print("1. To solve a sudoku in a textfile:\n")
    print("$ python3 sudokub.py 'textfile'\n")
    print("2. To solve all sudokus from a repository:\n")
    print("$ python3 sudokub.py 'repository'\n")
    print("3. To generate a sudoku of a given size:\n")
    print("$ python3 sudokub.py -generate 'size'\n")

if __name__ == '__main__':
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print_program_use()
        exit()

    # Generates a sudoku of a given size.
    if len(sys.argv) == 3:
        if sys.argv[1] == "-generate":
            generate_sudoku(int(sys.argv[2]))
        else:
            print_program_use()

    else:
        # The argument is a directory.
        if os.path.isdir(sys.argv[1]):
            files = os.listdir(sys.argv[1])
            nbfiles = len(glob.glob1(sys.argv[1] + '/', "*.txt"))
            counter = 0

            for f in files:
                if f.endswith(".txt"):
                    # Gets the filename without its extension
                    filename = os.path.splitext(f)[0]
                    sudoku = sudoku_read(sys.argv[1] + "/" + str(f))

                    myfile = open("sudoku.cnf", 'w')
                    N = len(sudoku)
                    myfile.write("p cnf "+str(N)+str(N)+str(N)+" "+
                        str(sudoku_constraints_number(sudoku))+"\n")
                    sudoku_generic_constraints(myfile, N)
                    sudoku_specific_constraints(myfile, sudoku)
                    myfile.close()

                    sudoku = sudoku_solve("sudoku.cnf")
                    outputfile = open(sys.argv[1] + "/" + str(filename) + ".sol", "w")

                    # Prints the sudoku in a .sol file matching the initial sudoku filename.
                    sudoku_print(outputfile, sudoku)
                    outputfile.close()
                    print_loading_bar(counter + 1, nbfiles)
                    counter += 1

            print("Your solutions are available in the " + sys.argv[1] + "directory.\n")

        # The argument is a file.
        else:
            sudoku = sudoku_read(str(sys.argv[1]))
            sudoku_print(sys.stdout, sudoku)

            myfile = open("sudoku.cnf", 'w')
            N = len(sudoku)
            myfile.write("p cnf "+str(N)+str(N)+str(N)+" "+
                        str(sudoku_constraints_number(sudoku))+"\n")
            sudoku_generic_constraints(myfile, N)
            sudoku_specific_constraints(myfile, sudoku)
            myfile.close()
            sys.stdout.write("cnf written in sudoku.cnf\n")
            sys.stdout.write("launching SAT solver\n")
            sudoku = sudoku_solve("sudoku.cnf")
            sudoku_print(sys.stdout, sudoku)
            sys.stdout.write("done\n")
