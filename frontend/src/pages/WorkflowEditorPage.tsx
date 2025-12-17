import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { workflowsApi } from "../services/api";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Spinner } from "../components/ui/spinner";
import WorkflowEditor from "../components/WorkflowEditor";
import {
  ArrowLeftIcon,
  DevicePhoneMobileIcon,
} from "@heroicons/react/24/solid";
import { PageLoader } from "../components/PageLoader";

export default function WorkflowEditorPage() {
  const { id } = useParams<{ id: string }>();
  const isNew = !id || id === "new";
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [workflowConfig, setWorkflowConfig] = useState<any>(null);

  // Fetch existing workflow if editing
  const { data: workflow, isLoading } = useQuery({
    queryKey: ["workflow", id],
    queryFn: () => workflowsApi.get(parseInt(id!)).then((res) => res.data),
    enabled: !isNew,
  });

  // Populate state when workflow data loads
  useEffect(() => {
    if (workflow) {
      setName(workflow.name);
      setDescription(workflow.description || "");
      setWorkflowConfig(workflow.config);
    }
  }, [workflow]);

  const saveMutation = useMutation({
    mutationFn: (data: any) => {
      if (isNew) {
        return workflowsApi.create(data);
      } else {
        return workflowsApi.update(parseInt(id!), data);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
      navigate("/workflows");
    },
  });

  const handleSave = () => {
    if (!name) return;

    saveMutation.mutate({
      name,
      description,
      config: workflowConfig,
      is_template: false,
    });
  };

  if (isLoading) {
    return <PageLoader />;
  }

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="border-b bg-white px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/workflows")}
          >
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="h-6 w-px bg-neutral-200" />
          <div className="flex items-center gap-2">
            <div className="space-y-1">
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Workflow Name"
                className="h-8 font-medium"
              />
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            onClick={handleSave}
            disabled={saveMutation.isPending || !name}
          >
            {saveMutation.isPending && <Spinner size="sm" className="mr-2" />}
            Save Workflow
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 border-r bg-white p-4 overflow-y-auto">
          <div className="space-y-4">
            <div>
              <Label>Description</Label>
              <Textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe what this workflow does..."
                rows={3}
                className="mt-1.5"
              />
            </div>

            <div className="rounded-lg bg-blue-50 p-4">
              <h4 className="flex items-center font-medium text-blue-900 mb-2">
                <DevicePhoneMobileIcon className="h-4 w-4 mr-2" />
                Workflow Tips
              </h4>
              <ul className="text-sm text-blue-800 space-y-2 list-disc pl-4">
                <li>
                  Start with a <strong>Validate</strong> node to check lead
                  data.
                </li>
                <li>
                  Use <strong>SMS Agent</strong> nodes to generate messages.
                </li>
                <li>Connect nodes to define the flow.</li>
                <li>
                  End with an <strong>End</strong> node.
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Editor Canvas */}
        <div className="flex-1 bg-neutral-50">
          <WorkflowEditor
            initialNodes={workflowConfig?.nodes}
            initialEdges={workflowConfig?.edges}
            onChange={(nodes, edges) => setWorkflowConfig({ nodes, edges })}
          />
        </div>
      </div>
    </div>
  );
}
