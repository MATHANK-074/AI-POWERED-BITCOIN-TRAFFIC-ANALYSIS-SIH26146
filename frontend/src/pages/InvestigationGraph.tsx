import React, { useEffect, useState, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import { getGraph, searchGraphPath } from '../services/api';
import { CytoscapeGraphData } from '../types';
import { EvidencePanel } from '../components/EvidencePanel';
import { Network, Search, RefreshCw, Info, GitCommit, ShieldAlert } from 'lucide-react';

export const InvestigationGraph: React.FC = () => {
  const [graphData, setGraphData] = useState<CytoscapeGraphData>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [centerNode, setCenterNode] = useState('');
  const [sourceNode, setSourceNode] = useState('');
  const [targetNode, setTargetNode] = useState('');
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [showEvidence, setShowEvidence] = useState<string | null>(null);
  const cyRef = useRef<any>(null);

  const fetchGraph = async (nodeId?: string) => {
    setLoading(true);
    try {
      const data = await getGraph(nodeId || undefined);
      setGraphData(data.graph);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePathSearch = async () => {
    if (!sourceNode || !targetNode) return;
    setLoading(true);
    try {
      const data = await searchGraphPath(sourceNode, targetNode);
      if (data.path_found && data.graph) {
        setGraphData(data.graph);
      } else {
        alert(`No path found between ${sourceNode} and ${targetNode}`);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, []);

  const elements = [
    ...graphData.nodes.map((n) => ({
      data: {
        id: n.data.id,
        label: n.data.label,
        type: n.data.type,
        anomaly: n.data.anomaly_score || 0,
        is_anomaly: n.data.is_anomaly || false,
      },
    })),
    ...graphData.edges.map((e) => ({
      data: {
        id: e.data.id,
        source: e.data.source,
        target: e.data.target,
        label: e.data.relationship,
      },
    })),
  ];

  const layout = {
    name: 'cose',
    animate: false,
    padding: 30,
  };

  const stylesheet = [
    {
      selector: 'node',
      style: {
        label: 'data(label)',
        'background-color': '#0369a1',
        color: '#0f172a',
        'font-size': '10px',
        'text-valign': 'bottom',
        'text-margin-y': 4,
        width: '30px',
        height: '30px',
      },
    },
    {
      selector: 'node[type = "Wallet"]',
      style: {
        'background-color': '#8b5cf6',
      },
    },
    {
      selector: 'node[type = "IP"]',
      style: {
        'background-color': '#06b6d4',
      },
    },
    {
      selector: 'node[is_anomaly = true]',
      style: {
        'background-color': '#f43f5e',
        borderWidth: '3px',
        borderColor: '#fda4af',
      },
    },
    {
      selector: 'edge',
      style: {
        width: 1.5,
        'line-color': '#475569',
        'target-arrow-color': '#475569',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        label: 'data(label)',
        'font-size': '8px',
        color: '#475569',
      },
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header controls */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-brand-900 flex items-center gap-2">
            <Network className="w-5 h-5 text-brand-600" />
            Interactive Investigation Graph
          </h2>
          <p className="text-xs text-content-500 mt-1">
            Cytoscape.js link analysis visualizing multi-hop relationships between IP observations, Transactions, and Wallets.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Path Search */}
          <div className="flex items-center gap-1.5 bg-surface-50 p-1 rounded-lg border border-surface-300">
            <input
              type="text"
              placeholder="Source Node ID..."
              value={sourceNode}
              onChange={(e) => setSourceNode(e.target.value)}
              className="bg-transparent text-xs text-brand-900 px-2 py-1 focus:outline-none w-28"
            />
            <span className="text-content-400 text-xs">→</span>
            <input
              type="text"
              placeholder="Target Node ID..."
              value={targetNode}
              onChange={(e) => setTargetNode(e.target.value)}
              className="bg-transparent text-xs text-brand-900 px-2 py-1 focus:outline-none w-28"
            />
            <button
              onClick={handlePathSearch}
              className="px-2.5 py-1 bg-purple-600 hover:bg-purple-500 text-brand-900 text-xs font-medium rounded transition-all flex items-center gap-1"
            >
              <GitCommit className="w-3.5 h-3.5" /> Find Path
            </button>
          </div>

          {/* Subgraph focus */}
          <div className="flex items-center gap-1.5">
            <input
              type="text"
              placeholder="Focus node ID..."
              value={centerNode}
              onChange={(e) => setCenterNode(e.target.value)}
              className="bg-surface-50 border border-surface-300 rounded-lg px-3 py-1.5 text-xs text-brand-900 placeholder-slate-500 focus:outline-none focus:border-brand-500 w-36"
            />
            <button
              onClick={() => fetchGraph(centerNode)}
              className="px-3.5 py-1.5 bg-brand-600 hover:bg-brand-500 text-brand-900 text-xs font-medium rounded-lg transition-all flex items-center gap-1.5"
            >
              <Search className="w-3.5 h-3.5" /> Subgraph
            </button>
            <button
              onClick={() => { setCenterNode(''); setSourceNode(''); setTargetNode(''); fetchGraph(); }}
              className="p-1.5 bg-surface-200 hover:bg-surface-300 text-content-600 rounded-lg transition-all"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Cytoscape Canvas */}
        <div className="lg:col-span-3 bg-surface-100 border border-surface-300 rounded-xl overflow-hidden h-[550px] relative shadow-lg">
          {loading ? (
            <div className="absolute inset-0 bg-surface-100 flex items-center justify-center text-xs text-content-500">
              Building graph topology...
            </div>
          ) : (
            <CytoscapeComponent
              elements={elements}
              style={{ width: '100%', height: '100%' }}
              layout={layout}
              stylesheet={stylesheet as any}
              cy={(cy) => {
                cyRef.current = cy;
                cy.on('tap', 'node', (evt) => {
                  setSelectedNode(evt.target.data());
                });
              }}
            />
          )}
        </div>

        {/* Selected Node Details Panel */}
        <div className="bg-surface-100 border border-surface-300 p-5 rounded-xl flex flex-col justify-between shadow-lg">
          <div>
            <h3 className="text-sm font-semibold text-brand-900 mb-4 flex items-center gap-2">
              <Info className="w-4 h-4 text-brand-600" /> Graph Element Inspector
            </h3>
            {!selectedNode ? (
              <p className="text-xs text-content-400 py-10 text-center">
                Click any node in the graph canvas to inspect its details, risk metrics, and audit evidence.
              </p>
            ) : (
              <div className="space-y-3 font-mono text-xs">
                <div className="p-3 bg-surface-50 rounded-lg">
                  <span className="text-[10px] text-content-400 block">Node ID</span>
                  <span className="text-xs font-bold text-brand-600 break-all">{selectedNode.id}</span>
                </div>
                <div className="p-3 bg-surface-50 rounded-lg">
                  <span className="text-[10px] text-content-400 block">Type</span>
                  <span className="text-xs font-bold text-brand-900">{selectedNode.type}</span>
                </div>
                <div className="p-3 bg-surface-50 rounded-lg">
                  <span className="text-[10px] text-content-400 block">Anomaly Score</span>
                  <span className="text-xs font-bold text-warning-600">{selectedNode.anomaly || 0}</span>
                </div>
                <button
                  onClick={() => setShowEvidence(selectedNode.id)}
                  className="w-full mt-2 py-2 bg-critical-600/20 hover:bg-critical-600/30 text-critical-600 border border-critical-500 font-semibold text-xs rounded-lg transition-all flex items-center justify-center gap-1.5"
                >
                  <ShieldAlert className="w-3.5 h-3.5" /> View Evidence Audit
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {showEvidence && (
        <EvidencePanel entityId={showEvidence} onClose={() => setShowEvidence(null)} />
      )}
    </div>
  );
};

