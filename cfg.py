import networkx as nx
import matplotlib.pyplot as plt

def print_graph(graph):

    pos = nx.shell_layout(graph)
    nx.draw(graph, pos, font_size=5, with_labels=False)
    for p in pos:
        pos[p][1] += 0.10
    nx.draw_networkx_labels(graph, pos)
    plt.show()
    
def psuedo_list(list):

    psuedo = []
    for element in list: psuedo.append(element)
    
    psuedo.pop(0)
    return psuedo
    
def get_opcodes(path):

    f = open(path,'r')
    
    opcodes = []
    iter_opcodes = []
    for line in f:
        line = line.strip().split("//")[0]
        if "Code:" in line and len(iter_opcodes)>0:
            opcodes.append(psuedo_list(iter_opcodes))
            iter_opcodes.clear()
        elif ":" in line and not line.isspace():
            iter_opcodes.append(line.split())
    opcodes.append(psuedo_list(iter_opcodes))

    return opcodes
    
def is_jump_op(opcode):
    if_jumps = ['if_acmpeq','if_acmpne','if_icmpeq','if_icmpge','if_icmpgt','if_icmple','if_icmplt','if_icmpne','ifeq','ifge','ifgt','ifle','iflt','ifne','ifnonnull','ifnull']
            
    if opcode in if_jumps:
        return True
    else:
        return False
        
def is_goto(opcode):
    if "goto" in opcode:
        return True
    else:
        return False
        
def get_jump_edge(opcodes, opcode, count):
    jump_edge = []
    goto = opcode[2]
    for i in range(len(opcodes)):
        if goto == (opcodes[i][0]).strip(":"):
            jump_edge = [opcode[1]+str(count), opcodes[i][1]+str(i+1)]
            break
    return jump_edge
    
    
def get_edges(opcodes):

    count = 0
    root = (opcodes.pop(0))[1]
    prev = root
    edges = []
    
    for opcode in opcodes:
        count+=1
        current = opcode[1]
        if is_goto(prev):
            prev = current
        elif is_goto(current):
            edges.append([prev+str(count-1), current+str(count)])
            edges.append(get_jump_edge(opcodes, opcode, count))
            prev = current
        elif is_jump_op(current):
            edges.append([prev+str(count-1), current+str(count)])
            edges.append(get_jump_edge(opcodes, opcode, count))
            prev = current
        else:
            edges.append([prev+str(count-1), current+str(count)])
            prev = current
        
        
    return edges
    
def create_graph(edges):

    graph = nx.DiGraph()
    for edge in edges:
        graph.add_edge(edge[0], edge[1])
    return graph
    
    
    
    
    
opcodes = get_opcodes('CWE129OP.txt')

for classes in opcodes:

    edges = get_edges(classes)
            
    graph = create_graph(edges)

    print_graph(graph)






