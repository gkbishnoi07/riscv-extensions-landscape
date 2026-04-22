"""
RISC-V Mentorship Coding Challenge
Tier 3 - Extension Sharing Graph
"""

import json
import sys
from collections import defaultdict


def build_graph(filepath):
    """Build extension-sharing graph from instr_dict.json."""
    with open(filepath) as f:
        data = json.load(f)

    edges = defaultdict(set)
    nodes = set()

    for mnemonic, info in data.items():
        exts = info.get("extension", [])
        nodes.update(exts)
        for i in range(len(exts)):
            for j in range(i + 1, len(exts)):
                key = tuple(sorted([exts[i], exts[j]]))
                edges[key].add(mnemonic.upper())

    return nodes, edges


def print_text_graph(nodes, edges):
    print("\n" + "=" * 70)
    print("EXTENSION SHARING GRAPH (text)")
    print("Edges = extensions that share at least one instruction")
    print("=" * 70)

    if not edges:
        print("  No shared instructions found.")
        return

    print(f"\n  Total extensions (nodes) : {len(nodes)}")
    print(f"  Total sharing pairs (edges) : {len(edges)}")
    print()
    print(f"  {'EXTENSION A':<25} {'EXTENSION B':<25} {'SHARED COUNT':>5}  EXAMPLE")
    print("  " + "-" * 70)

    for (a, b), shared in sorted(edges.items(), key=lambda x: -len(x[1])):
        example = sorted(shared)[0]
        print(f"  {a:<25} {b:<25} {len(shared):>5}  e.g. {example}")

    print("=" * 70)


def generate_html_graph(nodes, edges, output_path):
    """Generate an interactive HTML graph using D3.js force layout."""

    nodes_list = sorted(nodes)

    js_nodes = []
    for n in nodes_list:
        if n.startswith("rv_v") or n.startswith("rv_zvk") or n.startswith("rv_zvb"):
            group = 1
        elif "zk" in n or "zbk" in n:
            group = 2
        elif n.startswith("rv_z"):
            group = 3
        elif n.startswith("rv64_"):
            group = 4
        elif n.startswith("rv32_"):
            group = 5
        else:
            group = 6
        js_nodes.append(f'{{"id":"{n}","group":{group}}}')

    js_links = []
    for (a, b), shared in edges.items():
        weight = len(shared)
        js_links.append(
            f'{{"source":"{a}","target":"{b}",'
            f'"value":{weight},"shared":{json.dumps(sorted(shared)[:5])}}}'
        )

    nodes_json = "[" + ",".join(js_nodes) + "]"
    links_json = "[" + ",".join(js_links) + "]"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>RISC-V Extension Sharing Graph</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@300;600&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0a0e1a;
    color: #e0e6f0;
    font-family: 'Space Grotesk', sans-serif;
    overflow: hidden;
  }}
  #header {{
    position: fixed; top: 0; left: 0; right: 0;
    padding: 14px 24px;
    background: rgba(10,14,26,0.92);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255,255,255,0.07);
    z-index: 10;
    display: flex; align-items: center; gap: 16px;
  }}
  #header h1 {{
    font-size: 15px; font-weight: 600; letter-spacing: 0.05em;
    color: #7ee8fa;
  }}
  #header span {{
    font-size: 12px; color: rgba(255,255,255,0.4);
    font-family: 'JetBrains Mono', monospace;
  }}
  #stats {{
    margin-left: auto; display: flex; gap: 20px;
  }}
  .stat {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; color: rgba(255,255,255,0.5);
  }}
  .stat b {{ color: #7ee8fa; font-size: 14px; }}
  #tooltip {{
    position: fixed;
    background: rgba(10,14,26,0.95);
    border: 1px solid rgba(126,232,250,0.3);
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.15s;
    max-width: 280px;
    z-index: 100;
    line-height: 1.6;
  }}
  #legend {{
    position: fixed; bottom: 20px; left: 20px;
    background: rgba(10,14,26,0.88);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 12px 16px;
    font-size: 11px;
  }}
  #legend h3 {{ font-size: 10px; color: rgba(255,255,255,0.4);
    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }}
  .legend-item {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; }}
  .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
  svg {{ position: fixed; top: 0; left: 0; }}
  line {{ stroke-opacity: 0.5; }}
  circle {{ cursor: pointer; transition: r 0.1s; }}
  circle:hover {{ stroke: white; stroke-width: 1.5px; }}
  text {{ font-family: 'JetBrains Mono', monospace; pointer-events: none; }}
</style>
</head>
<body>
<div id="header">
  <h1>RISC-V Extension Sharing Graph</h1>
  <span>Edges = shared instructions between extensions</span>
  <div id="stats">
    <div class="stat"><b>{len(nodes_list)}</b><br>extensions</div>
    <div class="stat"><b>{len(edges)}</b><br>edges</div>
  </div>
</div>
<div id="tooltip"></div>
<div id="legend">
  <h3>Extension Groups</h3>
  <div class="legend-item"><div class="legend-dot" style="background:#00d4ff"></div>Vector / Crypto-Vector</div>
  <div class="legend-item"><div class="legend-dot" style="background:#ffd700"></div>Cryptography (Zk*)</div>
  <div class="legend-item"><div class="legend-dot" style="background:#4a9eff"></div>Z-extensions</div>
  <div class="legend-item"><div class="legend-dot" style="background:#b44aff"></div>RV64-specific</div>
  <div class="legend-item"><div class="legend-dot" style="background:#ff8c42"></div>RV32-specific</div>
  <div class="legend-item"><div class="legend-dot" style="background:#8899aa"></div>Base / Other</div>
</div>
<svg id="graph"></svg>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
const NODES = {nodes_json};
const LINKS = {links_json};

const COLORS = [null,
  "#00d4ff", "#ffd700", "#4a9eff",
  "#b44aff", "#ff8c42", "#8899aa"
];

const W = window.innerWidth, H = window.innerHeight;
const svg = d3.select("#graph").attr("width", W).attr("height", H);
const g = svg.append("g");

svg.call(d3.zoom().scaleExtent([0.1, 6]).on("zoom", e => g.attr("transform", e.transform)));

const sim = d3.forceSimulation(NODES)
  .force("link", d3.forceLink(LINKS).id(d => d.id).distance(d => 80 - d.value * 2).strength(0.4))
  .force("charge", d3.forceManyBody().strength(-180))
  .force("center", d3.forceCenter(W / 2, H / 2))
  .force("collision", d3.forceCollide(18));

const link = g.append("g").selectAll("line")
  .data(LINKS).join("line")
  .attr("stroke", d => d.value > 5 ? "#ffd700" : d.value > 2 ? "#4a9eff44" : "#ffffff18")
  .attr("stroke-width", d => Math.min(1 + d.value * 0.3, 4));

const node = g.append("g").selectAll("g")
  .data(NODES).join("g")
  .call(d3.drag()
    .on("start", (e,d) => {{ if(!e.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; }})
    .on("drag",  (e,d) => {{ d.fx=e.x; d.fy=e.y; }})
    .on("end",   (e,d) => {{ if(!e.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }}));

node.append("circle")
  .attr("r", 7)
  .attr("fill", d => COLORS[d.group])
  .attr("fill-opacity", 0.85);

node.append("text")
  .attr("dx", 10).attr("dy", 4)
  .attr("fill", "rgba(255,255,255,0.55)")
  .attr("font-size", "9px")
  .text(d => d.id.replace(/^rv(?:32|64)?_/, ''));

const tip = document.getElementById("tooltip");

node
  .on("mouseover", (e, d) => {{
    const connected = LINKS
      .filter(l => l.source.id === d.id || l.target.id === d.id)
      .map(l => {{
        const other = l.source.id === d.id ? l.target.id : l.source.id;
        return `<div style="color:#aaa">${{other}}: <span style="color:#7ee8fa">${{l.value}} shared</span></div>`;
      }}).join("");
    tip.innerHTML = `<b style="color:#7ee8fa">${{d.id}}</b><br><br>${{connected || "No connections"}}`;
    tip.style.opacity = 1;
  }})
  .on("mousemove", e => {{
    tip.style.left = (e.clientX + 14) + "px";
    tip.style.top  = (e.clientY - 10) + "px";
  }})
  .on("mouseout", () => tip.style.opacity = 0);

sim.on("tick", () => {{
  link
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
}});
</script>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)

    print(f"\n  HTML graph saved to: {output_path}")
    print("     Open it in your browser")


def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "../src/instr_dict.json"
    output = sys.argv[2] if len(sys.argv) > 2 else "graph.html"

    print(f"\nBuilding extension sharing graph from: {filepath}")
    nodes, edges = build_graph(filepath)

    print_text_graph(nodes, edges)
    generate_html_graph(nodes, edges, output)


if __name__ == "__main__":
    main()
