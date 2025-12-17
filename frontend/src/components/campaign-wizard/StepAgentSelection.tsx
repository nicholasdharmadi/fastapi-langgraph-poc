import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { agentsApi } from "../../services/api";
import { Button } from "../ui/button";
import {
  PlusIcon,
  CpuChipIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/solid";
import { Spinner } from "../ui/spinner";
import { cn } from "../../lib/utils";

interface StepAgentSelectionProps {
  selectedAgentId: number | null;
  onSelect: (agentId: number) => void;
}

export function StepAgentSelection({
  selectedAgentId,
  onSelect,
}: StepAgentSelectionProps) {
  const navigate = useNavigate();
  const { data: agents, isLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: () => agentsApi.list().then((res) => res.data),
  });

  if (isLoading)
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );

  return (
    <div className="space-y-6 py-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {agents?.map((agent) => (
          <div
            key={agent.id}
            className={cn(
              "relative border rounded-lg p-4 cursor-pointer transition-all hover:border-neutral-400",
              selectedAgentId === agent.id
                ? "border-neutral-900 bg-neutral-50 ring-1 ring-neutral-900"
                : "border-neutral-200"
            )}
            onClick={() => onSelect(agent.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white rounded-md border shadow-sm">
                  <CpuChipIcon className="h-6 w-6 text-neutral-900" />
                </div>
                <div>
                  <h3 className="font-medium text-neutral-900">{agent.name}</h3>
                  <p className="text-xs text-neutral-500">{agent.model}</p>
                </div>
              </div>
              {selectedAgentId === agent.id && (
                <CheckCircleIcon className="h-6 w-6 text-neutral-900" />
              )}
            </div>
            <p className="mt-3 text-sm text-neutral-600 line-clamp-2">
              {agent.description || "No description provided."}
            </p>
            <div className="mt-3 flex gap-2">
              {agent.capabilities.map((cap) => (
                <span
                  key={cap}
                  className="px-2 py-0.5 bg-neutral-100 border border-neutral-200 rounded text-xs font-medium uppercase tracking-wider text-neutral-900"
                >
                  {cap}
                </span>
              ))}
            </div>
          </div>
        ))}

        <div className="border border-dashed border-neutral-300 rounded-lg p-4 flex flex-col items-center justify-center text-center hover:bg-neutral-50 cursor-pointer min-h-[160px]">
          <div className="p-2 bg-neutral-100 rounded-full mb-2">
            <PlusIcon className="h-6 w-6 text-neutral-900" />
          </div>
          <h3 className="font-medium text-neutral-900">Create New Agent</h3>
          <p className="text-xs text-neutral-500 mt-1">
            Configure a new AI assistant
          </p>
          <Button
            variant="link"
            size="sm"
            className="mt-2 text-neutral-900"
            onClick={(e) => {
              e.stopPropagation();
              navigate("/agents");
            }}
          >
            Go to Agents Page
          </Button>
        </div>
      </div>
    </div>
  );
}
