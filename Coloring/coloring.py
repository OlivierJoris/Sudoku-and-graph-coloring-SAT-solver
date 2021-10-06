#!/usr/bin/python

import sys
import subprocess

class Tgraph:
  def __init__(self, nodes, edges):
    self.nodes = nodes
    self.edges = edges
    self.colors = {}
    self.status = 0

# reads a graph, one edge per line, one space between node
def graph_read(filename):
    myfile = open(filename, 'r')
    graph = Tgraph([], [])
    for line in myfile:
        if line == "" or line[0] == '#':
            continue
        line = line.split(" ")
        sys.stdout.write(line[1])
        if len(line) != 2 or line[1][len(line[1]) - 1] != '\n':
            exit("illegal input\n")
        line[1] = line[1][0:len(line[1]) - 1]
        if not line[0] in graph.nodes:
            graph.nodes += [ line[0] ]
        if not line[1] in graph.nodes:
            graph.nodes += [ line[1] ]
        graph.edges += [ (line[0], line[1]) ]
    return graph

def graph_print(myfile, graph):

    def node_color(node):
        if node in graph.colors:
            return node + " (" + str(graph.colors[node]) + ")"
        else:
            return node

    myfile.write("Number of nodes:" + str(len(graph.nodes)) + "\n")
    myfile.write("Number of edges:" + str(len(graph.edges)) + "\n")
    myfile.write("Nodes\n")
    for node in graph.nodes:
        myfile.write("  " + node_color(node) + "\n")

    myfile.write("Edges\n")
    for (node1, node2) in graph.edges:
        myfile.write("  " + node_color(node1) + "--" + node_color(node2) + "\n")

    if graph.status < 0:
        myfile.write("Recently showed to be uncolorizable with " +
                     str(-graph.status) + " colors\n")
    elif graph.status > 0:
        myfile.write("Colorizable with " + str(graph.status) + " colors\n")
        myfile.write("[")
        for node in graph.nodes:
          myfile.write('("'+node+'",'+str(graph.colors[node]) + '),')
        myfile.write("]\n")
        
# prints the constraints for graph coloring with n colors
def graph_constraints(myfile, graph, nc):

    def output(s):
        myfile.write(s)

    def newposlit(n,c):
        output(str(n * nc + c + 1) + " ")

    def newneglit(n,c):
        output(str(-(n * nc + c + 1)) + " ")

    def newcl():
        output("0\n")

    def newcomment(s):
#        output("c %s\n"%s)
        output("")

    nn = len(graph.nodes)
    ne = len(graph.edges)

    myfile.write("p cnf "+str(nn * nc)+" "+
                 str(nn + nn * nc * (nc - 1) // 2 + ne * nc)+"\n")
                 
    # every node has one color
    for node1 in range(nn):
        for colour in range(nc):
            newposlit(node1, colour)
        newcl()

    # every node has at most one color
    for node1 in range(nn):
        for colour1 in range(nc):
            for colour2 in range(colour1 + 1, nc):
                newneglit(node1, colour1)
                newneglit(node1, colour2)
                newcl()

    # no edge with the same color
    for edge1, edge2 in graph.edges:
        for colour in range(nc):
            newneglit(graph.nodes.index(edge1), colour)
            newneglit(graph.nodes.index(edge2), colour)
            newcl()

def graph_solve(filename, graph, nc):
    command = "java -jar org.sat4j.core.jar " + filename
    process = subprocess.Popen(command, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    nn = len(graph.nodes)
    for line in out.split(b'\n'):
        line = line.decode("utf-8")
        if line == "" or line[0] == 'c':
            continue
        if line[0] == 's':
            if line != 's SATISFIABLE':
                graph.status = -nc
                return graph
            continue
        if line[0] == 'v':
            line = line[2:]
            units = line.split()
            if units.pop() != '0':
                exit("strange output from SAT solver:" + line + "\n")
            units = [int(x) for x in units if int(x) >= 0]
            for number in units:
                graph.colors[graph.nodes[(number - 1) // nc]] = (number - 1) % nc + 1
                graph_print(sys.stdout, graph)
            graph.status = nc
            return graph
        exit("strange output from SAT solver:" + line + "\n")
        return None

if len(sys.argv) != 2:
    exit("This program requires exactly one argument (file with the graph)\n")

graph = graph_read(str(sys.argv[1]))
graph_print(sys.stdout, graph)

myfile = open("graph.cnf", 'w')
graph_constraints(myfile, graph, 4)
myfile.close()
sys.stdout.write("cnf written in graph.cnf\n")
sys.stdout.write("launching SAT solver\n")
graph = graph_solve("graph.cnf", graph, 4)
sys.stdout.write("solved\n")
graph_print(sys.stdout, graph)
sys.stdout.write("done\n")
