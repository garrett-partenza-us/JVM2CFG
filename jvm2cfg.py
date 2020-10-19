
import networkx as nx
import matplotlib.pyplot as plt
from itertools import groupby
import random
import string


class method_obj:

    name = None
    id = None
    opcodes = None
    edges = None
    graph = None
    returns = []
    first = None
    
    
def break_opcode(instruction):
    
    instruction = instruction.strip()
    opcode_parts = []
    parts = instruction.split(':')
    op1 = (parts.pop(0))
    parts = parts[0].split('//')
    op4 = None
    if len(parts) > 1:
        op4 = parts[1]
    parts = parts[0]
    parts = parts.split()
    op2 = parts[0]
    op3 = None
    if len(parts)>1: op3 = parts[1]
    opcode_parts.append(op1)
    opcode_parts.append(op2)
    opcode_parts.append(op3)
    opcode_parts.append(op4)
    opcode_parts.append(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)))


    return opcode_parts
    
    
def bytomize(method):
    
    object = method_obj()
    header = method.pop(0)
    object.name = header
    if len(header.split())== 4:
        object.id = header.split()[3]
    method.pop(0)
    
    opcodes = []
    r = []
    
    for instruction in method:
    
        if instruction == "Exception table:":
            break
        else:
            try:
                a = break_opcode(instruction)
                if "return" in a[1]:
                    r.append(opcode_toString(a))
                opcodes.append(a)
            except:
                print("Failed bytomize for instruction: "+str(instruction))
    
    object.opcodes = opcodes
    object.returns = r
    if len(object.opcodes)>0:
        object.first = opcode_toString(opcodes[0])
        
    return object

def get_opcodes(path):
    lines = []
    with open(path) as file:
        lines = [line.strip() for line in file]
    
    #methods = [list(sub) for ele, sub in groupby(lines, key = bool) if ele]
    methods = []
    for i in range(len(lines)):
        if lines[i] == "Code:":
            s = i-1
            t = len(lines)-1
            for j in range(i+1, len(lines)):
                if lines[j] == "Code:":
                    t = j-2
                    break
            add = lines[s:t]
            methods.append(add)

        
            
    
    objects = []
    for method in methods:
        objects.append(bytomize(method))
        
    return objects
    
def is_if(opcode):
    ifs = ['if_acmpeq','if_acmpne','if_icmpeq','if_icmpge','if_icmpgt','if_icmple','if_icmplt','if_icmpne','ifeq','ifge','ifgt','ifle','iflt','ifne','ifnonnull','ifnull']
    if opcode in ifs:
        return True
    return False
    
def is_goto(opcode):

    if opcode == "goto":
        return True
    return False

def is_invokestatic(opcode):
    
    if opcode == "invokestatic":
        return True
    return False

def get_edges(method):

    
        
    edges = []
    
    for i in range(len(method.opcodes)):
        id = method.opcodes[i][0]
        opcode = method.opcodes[i][1]
        goto = method.opcodes[i][2]
        comment = method.opcodes[i][3]

        if is_if(opcode):
            edges.append([id, goto])
            edges.append([id, method.opcodes[i+1][0]])
        elif is_goto(opcode):
            edges.append([id, goto])
        else:
            try:
                edges.append([id, method.opcodes[i+1][0]])
            except:
                pass
        
    method.edges = edges
    
def opcode_toString(opcode):
    joiners = []
    joiners.append(str(opcode[0]))
    joiners.append(str(opcode[1]))
    if opcode[2] != None: joiners.append(str(opcode[2]))
    if opcode[3] != None: joiners.append(str(opcode[3]))
    joiners.append(opcode[4])
    return( ', '.join(joiners))

        
def generate_graph(method):
    
    g = nx.DiGraph()
    for edge in method.edges:
        s = edge[0]
        t = edge[1]
        gs = None
        gt = None
        
        for o in method.opcodes:
            if o[0] == s: gs = opcode_toString(o)
            if o[0] == t: gt = opcode_toString(o)
            
        g.add_edge(gs,gt)
        
    method.graph = g
    
def is_invokestatic(opcode):
    if opcode.strip() == "invokestatic":
        return True
    return False
    
def print_graph(graph):

    pos = nx.shell_layout(graph)
    nx.draw(graph, pos, font_size=5, with_labels=False)
    for p in pos:
        pos[p][1] += 0.10
    nx.draw_networkx_labels(graph, pos)
    plt.show()
    
def finish_graph(main, methods):
    edges = main.graph.edges()
    nodes = list(main.graph.nodes)
    for i in range(len(nodes)):
        node = nodes[i]
        if is_invokestatic(node.split(",")[1]):
            called = (node.split(",")[3]).split()[1]
            for method in methods:
                if method.id != None and str(called) in method.id:
                    c = nx.union(main.graph, method.graph)
                    c.add_edge(node, method.first)
                    neighbor = (list((main.graph).neighbors(node))[0])
                    for r in method.returns:
                        c.add_edge(r, neighbor)
                    c.remove_edge(node, neighbor)
                    main.graph = c
                    

                    
def connect_methods(methods):
    for method in methods:
        print(method.name)
        nodes = list(method.graph.nodes)
        for i in range(len(nodes)):
            node = nodes[i]
            if is_invokestatic(node.split(",")[1]):
                called = (node.split(",")[3]).split()[1]
                for submethod in methods:
                    if submethod.id != None and str(called) in submethod.id:
                        print("connected to "+submethod.id)
                        c = nx.union(method.graph, submethod.graph)
                        print("done")
                        c.add_edge(node, submethod.first)
                        neighbor = (list((method.graph).neighbors(node))[0])
                        for r in submethod.returns:
                            c.add_edge(r, neighbor)
                        c.remove_edge(node, neighbor)
                        method.graph = c
                        break
                        
                        


def connect_methods3(methods):
    dict = {}
    for m in methods:
        dict[m.name] = {}
    for method in methods:
        nodes = list(method.graph.nodes)
        subdict = {}
        for m in methods:
            subdict[m.name] = []
        for i in range(len(nodes)):
            node = nodes[i]
            if is_invokestatic(node.split(",")[1]):
                called = (node.split(",")[3]).split()[1]
                for submethod in methods:
                    if submethod.id != None and str(called) in submethod.id:
                        subdict[submethod.name].append(node)
        dict[method.name] = subdict
    
    final = nx.DiGraph()

    
    for m in methods:
        final = nx.union(final, m.graph)
    for nodes in final.nodes:
        if is_invokestatic(nodes.split(",")[1]):
            called = (nodes.split(",")[3]).split()[1]
            for m in methods:
                if m.id != None and str(called) in m.id:
                    neighbor = (list(final.neighbors(nodes))[0])
                    final.add_edge(nodes, m.first)
                    for r in m.returns:
                        final.add_edge(r, neighbor)
                    final.remove_edge(nodes, neighbor)
    return final
    
    
text_file = 'exampleOpcodes.txt'

methods = get_opcodes(text_file)

print("completed getting opcodes")

main = None
has_main = False




for method in methods:
    if "public static void main" in method.name:
        main = method
        has_main = True
        get_edges(main)
        generate_graph(main)
    else:
        get_edges(method)
        generate_graph(method)
        
    
if has_main:
    final_graph = connect_methods3(methods)
    a = nx.dfs_edges(final_graph, source=main.first, depth_limit=None)
    main_graph = nx.DiGraph()
    for b in a:
        main_graph.add_edge(b[0], b[1])
    result = main_graph
else:
    result = connect_methods3(methods)


