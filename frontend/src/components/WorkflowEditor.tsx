import { useState, useCallback, useEffect } from "react";
import ReactFlow, {
  Controls,
  Background,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  Node,
  Edge,
  NodeChange,
  EdgeChange,
  Connection,
  Panel,
} from "reactflow";
import "reactflow/dist/style.css";
import { Button } from "./ui/button";

const initialNodes: Node[] = [
  {
    id: "start",
    type: "input",
    data: { label: "Start Campaign" },
    position: { x: 250, y: 0 },
  },
  {
    id: "validate",
    data: { label: "Validate Leads" },
    position: { x: 250, y: 100 },
  },
  {
    id: "sms",
    data: { label: "Send SMS" },
    position: { x: 250, y: 200 },
  },
  {
    id: "end",
    type: "output",
    data: { label: "End" },
    position: { x: 250, y: 300 },
  },
];

const initialEdges: Edge[] = [
  { id: "e1-2", source: "start", target: "validate" },
  { id: "e2-3", source: "validate", target: "sms" },
  { id: "e3-4", source: "sms", target: "end" },
];

interface WorkflowEditorProps {
  initialNodes?: Node[];
  initialEdges?: Edge[];
  onChange?: (nodes: Node[], edges: Edge[]) => void;
}

export default function WorkflowEditor({
  initialNodes: propNodes,
  initialEdges: propEdges,
  onChange,
}: WorkflowEditorProps) {
  const [nodes, setNodes] = useState<Node[]>(propNodes || initialNodes);
  const [edges, setEdges] = useState<Edge[]>(propEdges || initialEdges);

  // Sync state when props change (e.g., when loading an existing workflow)
  useEffect(() => {
    if (propNodes) {
      setNodes(propNodes);
    }
  }, [propNodes]);

  useEffect(() => {
    if (propEdges) {
      setEdges(propEdges);
    }
  }, [propEdges]);

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      setNodes((nds) => {
        const newNodes = applyNodeChanges(changes, nds);
        onChange?.(newNodes, edges);
        return newNodes;
      });
    },
    [onChange, edges]
  );
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      setEdges((eds) => {
        const newEdges = applyEdgeChanges(changes, eds);
        onChange?.(nodes, newEdges);
        return newEdges;
      });
    },
    [onChange, nodes]
  );
  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => {
        const newEdges = addEdge(params, eds);
        onChange?.(nodes, newEdges);
        return newEdges;
      });
    },
    [onChange, nodes]
  );

  const addNode = (type: string, label: string) => {
    const id = `${type}-${Date.now()}`;
    const newNode: Node = {
      id,
      data: { label },
      position: { x: Math.random() * 400, y: Math.random() * 400 },
    };
    setNodes((nds) => {
      const newNodes = [...nds, newNode];
      onChange?.(newNodes, edges);
      return newNodes;
    });
  };

  return (
    <div className="h-[500px] w-full border rounded-lg bg-neutral-50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Controls />
        <Panel
          position="top-right"
          className="bg-white p-2 rounded shadow-sm flex gap-2"
        >
          <Button
            size="sm"
            variant="outline"
            onClick={() => addNode("default", "Enrich Data")}
          >
            + Enrich Data
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => addNode("default", "Send SMS")}
          >
            + Send SMS
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => addNode("default", "Voice Call")}
          >
            + Voice Call
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => addNode("default", "Wait")}
          >
            + Wait
          </Button>
        </Panel>
      </ReactFlow>
    </div>
  );
}
