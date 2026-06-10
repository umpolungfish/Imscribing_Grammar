import networkx as nx
import matplotlib.pyplot as plt
from itertools import product

# Core Z2 from original diagrams
G_z2 = nx.Graph()
nodes_z2 = ['spin-up', 'paired', 'empty', 'spin-down']
G_z2.add_nodes_from(nodes_z2)
G_z2.add_edges_from([('spin-up', 'paired'), ('spin-up', 'empty'), 
                     ('paired', 'spin-down'), ('empty', 'spin-down')])

print("Z2 Nodes:", nodes_z2)
print("Z2 Edges:", list(G_z2.edges()))

# Extend to SU(3) color
def add_su3_layer(G, base_node):
    colors = ['R', 'G', 'B']
    for c in colors:
        new_node = f"{base_node}_{c}"
        G.add_node(new_node)
        G.add_edge(base_node, new_node)
    return G

G_sm = G_z2.copy()
G_sm = add_su3_layer(G_sm, 'spin-up')  # Example layering

# Full SM hierarchy simulation stub
print("\n=== Full SM Extension ===")
print("Gauge groups: SU(3)_c x SU(2)_L x U(1)_Y")
print("Fermions: 3 generations, color + weak + hypercharge")
print("Bosons: 8 gluons + 3W + 1B + Higgs doublet")
print("Breaking: Higgs VEV enforces ceilings and antichain collapses")

pos = {'spin-up': (0,2), 'paired': (3,2), 'empty': (0,0), 'spin-down': (3,0)}
nx.draw(G_z2, pos, with_labels=True, node_color='gold', node_size=2500, font_size=12, font_weight='bold')
plt.title("Z2 Pauli/Hund Hierarchy")
plt.savefig("/home/workdir/artifacts/z2_diagram.png")
print("Diagram saved to workspace.")