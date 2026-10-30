import networkx as nx
import matplotlib.pyplot as plt
import re

def generate_call_graph(log_file: str, output="voynich_final_graph.png"):
    G = nx.DiGraph()
    print("Building FINAL smart call graph...")

    reg_pattern = re.compile(r'%r(\d+)')
    prev_regs = []

    with open(log_file, 'r') as f:
        for line in f:
            if '%r' not in line:
                continue
            current_regs = [int(x) for x in reg_pattern.findall(line)]
            if not current_regs:
                continue

            for r in current_regs:
                G.add_node(r)

            # Connect within instruction
            if 'FSPLIT' in line and len(current_regs) >= 3:
                src = current_regs[0]
                for dst in current_regs[1:]:
                    G.add_edge(src, dst, label="split")
            elif len(current_regs) > 1:
                for i in range(len(current_regs)-1):
                    G.add_edge(current_regs[i], current_regs[i+1])

            # Connect across lines
            if prev_regs and current_regs:
                G.add_edge(prev_regs[-1], current_regs[0], label="flow")

            prev_regs = current_regs

    print(f"Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Use weakly connected components for directed graph
    if G.number_of_nodes() > 0:
        largest_cc = max(nx.weakly_connected_components(G), key=len)
        G = G.subgraph(largest_cc).copy()
        print(f"Using largest connected component: {G.number_of_nodes()} nodes")

    # Draw
    plt.figure(figsize=(32, 32))
    pos = nx.spring_layout(G, k=0.1, iterations=100, seed=42)
    
    nx.draw(G, pos, 
            node_size=40, 
            alpha=0.85, 
            with_labels=True, 
            font_size=7, 
            node_color='lightblue',
            edge_color='darkgray',
            arrows=True,
            arrowsize=10)

    plt.title("Voynich Manuscript — Final IMASM Register Flow Graph\n"
              f"Connected component ({G.number_of_nodes()} nodes)")
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"\n✅ Graph saved as {output}")
    print("Open it and zoom heavily. You should now see connected chains.")

if __name__ == "__main__":
    generate_call_graph("full_untruncated_log.txt")