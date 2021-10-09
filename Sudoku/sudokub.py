#!/usr/bin/python

import sys
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
            if N != 4 and N != 9:
                exit("illegal input: only size 4 and 9 are supported\n")
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
        output(str(i)+str(j)+str(k)+ " ")

    def newcl():
        output("0\n")

    def newcomment(s):
#        output("c %s\n"%s)
        output("")

    if N == 9:
        n = 3
    elif N == 4:
        n = 2
    else:
        exit("Only supports size 9 and 4")

    # Each cell of the sudoku must contains stricly one number in [1, 9]
    for line in range(1, N + 1):
        for column in range(1, N + 1):
            for number in range(1, 10):
                newlit(line, column, number)    
            newcl()
    
    for line in range(1, N + 1):
        for column in range(1, N + 1):
            propositions = []
            for number in range(1, 10):
                propositions.append([line, column, number])

            for i in range(10):
                for p in propositions[i+1:]:
                    newlit(-propositions[i][0], propositions[i][1], propositions[i][2])
                    newlit(-p[0], p[1], p[2])
                    newcl()

def sudoku_specific_constraints(myfile, sudoku):

    def output(s):
        myfile.write(s)

    def newlit(i,j,k):
        output(str(i)+str(j)+str(k)+ " ")

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
            else:
                exit("strange output from SAT solver:" + line + "\n")
            sudoku = [ [0 for i in range(N)] for j in range(N)]
            for number in units:
                sudoku[number // 100 - 1][( number // 10 )% 10 - 1] = number % 10
            return sudoku
        exit("strange output from SAT solver:" + line + "\n")
        return []

if len(sys.argv) != 2:
    exit("This program requires exactly one argument (file with the sudoku)\n")

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
