import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { agentsApi, Agent } from "../services/api";
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CpuChipIcon,
  ChatBubbleBottomCenterTextIcon,
  PhoneIcon,
  WrenchScrewdriverIcon,
  SparklesIcon,
} from "@heroicons/react/24/solid";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Checkbox } from "../components/ui/checkbox";
import { Spinner } from "../components/ui/spinner";
import { PageLoader } from "../components/PageLoader";
import { formatDate } from "../lib/utils";
import { PromptSelector } from "../components/prompt-builder/PromptSelector";

export default function AgentsPage() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const { data: agents, isLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: () => agentsApi.list().then((res) => res.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => agentsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
      setDeleteId(null);
    },
  });

  if (isLoading) {
    return <PageLoader />;
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-neutral-900">
            AI Agents
          </h2>
          <p className="mt-2 text-neutral-600">
            Manage your AI agents, their personalities, and capabilities.
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <PlusIcon className="h-4 w-4" />
          New Agent
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {agents && agents.length > 0 ? (
          agents.map((agent) => (
            <Card key={agent.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2">
                    <div className="p-2 bg-neutral-100 rounded-lg text-neutral-900">
                      <CpuChipIcon className="h-6 w-6" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{agent.name}</CardTitle>
                      <CardDescription className="line-clamp-1">
                        {agent.model}
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setEditingAgent(agent)}
                    >
                      <PencilIcon className="h-4 w-4 text-neutral-900" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setDeleteId(agent.id)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-neutral-600 mb-4 line-clamp-2 h-10">
                  {agent.description || "No description provided."}
                </p>

                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm text-neutral-700">
                    <WrenchScrewdriverIcon className="h-4 w-4 text-neutral-900" />
                    <span className="font-medium">Capabilities:</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {agent.capabilities.includes("sms") && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-neutral-100 text-neutral-900 border border-neutral-200">
                        <ChatBubbleBottomCenterTextIcon className="h-3 w-3 mr-1 text-neutral-900" />
                        SMS
                      </span>
                    )}
                    {agent.capabilities.includes("voice") && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-neutral-100 text-neutral-900 border border-neutral-200">
                        <PhoneIcon className="h-3 w-3 mr-1 text-neutral-900" />
                        Voice
                      </span>
                    )}
                    {agent.capabilities.length === 0 && (
                      <span className="text-xs text-neutral-400 italic">
                        None configured
                      </span>
                    )}
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t text-xs text-neutral-400">
                  Created {formatDate(agent.created_at)}
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="col-span-full">
            <Card>
              <CardContent className="py-12 text-center text-neutral-500">
                No agents created yet. Create your first AI agent!
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {(showCreateModal || editingAgent) && (
        <AgentModal
          agent={editingAgent}
          onClose={() => {
            setShowCreateModal(false);
            setEditingAgent(null);
          }}
        />
      )}

      {/* Delete Confirmation */}
      <Dialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Agent?</DialogTitle>
            <DialogDescription>
              This action cannot be undone. This will permanently delete the
              agent and may affect campaigns using it.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteId(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => deleteId && deleteMutation.mutate(deleteId)}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function AgentModal({
  agent,
  onClose,
}: {
  agent: Agent | null;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const isEditing = !!agent;

  const [formData, setFormData] = useState({
    name: agent?.name || "",
    description: agent?.description || "",
    system_prompt: agent?.system_prompt || "You are a helpful AI assistant.",
    model: agent?.model || "gpt-4o",
    capabilities: agent?.capabilities || ["sms"],
    tools: agent?.tools || [],
  });

  const [showPromptSelector, setShowPromptSelector] = useState(false);

  const mutation = useMutation({
    mutationFn: (data: any) => {
      if (isEditing && agent) {
        return agentsApi.update(agent.id, data);
      }
      return agentsApi.create(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
      onClose();
    },
  });

  const toggleCapability = (cap: string, checked: boolean) => {
    setFormData((prev) => {
      const capabilities = Array.isArray(prev.capabilities)
        ? prev.capabilities
        : [];
      const newCapabilities = checked
        ? [...capabilities, cap]
        : capabilities.filter((c) => c !== cap);
      return { ...prev, capabilities: Array.from(new Set(newCapabilities)) };
    });
  };

  const handlePromptSelect = (promptText: string) => {
    setFormData({ ...formData, system_prompt: promptText });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? "Edit Agent" : "Create New Agent"}
          </DialogTitle>
          <DialogDescription>
            Configure your AI agent's personality and capabilities.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Agent Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                placeholder="e.g., Sales Bot 3000"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <select
                id="model"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={formData.model}
                onChange={(e) =>
                  setFormData({ ...formData, model: e.target.value })
                }
              >
                <option value="gpt-4o">GPT-4o</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              placeholder="Brief description of what this agent does"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="system_prompt">System Prompt</Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setShowPromptSelector(true)}
                className="text-xs"
              >
                <SparklesIcon className="h-3 w-3 mr-1" />
                Use Saved Prompt
              </Button>
            </div>
            <Textarea
              id="system_prompt"
              value={formData.system_prompt}
              onChange={(e) =>
                setFormData({ ...formData, system_prompt: e.target.value })
              }
              placeholder="You are a helpful assistant..."
              className="min-h-[150px] font-mono text-sm"
              required
            />
            <p className="text-xs text-neutral-500">
              Define the agent's personality, constraints, and knowledge base
              here.
            </p>
          </div>

          <PromptSelector
            open={showPromptSelector}
            onClose={() => setShowPromptSelector(false)}
            onSelect={handlePromptSelect}
          />

          <div className="space-y-3">
            <Label>Capabilities</Label>
            <div className="flex gap-4">
              <label className="flex items-center space-x-2 border p-3 rounded-md w-full hover:bg-neutral-50 transition-colors cursor-pointer">
                <Checkbox
                  checked={formData.capabilities.includes("sms")}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    toggleCapability("sms", e.target.checked)
                  }
                />
                <div className="flex items-center">
                  <ChatBubbleBottomCenterTextIcon className="h-4 w-4 mr-2 text-neutral-900" />
                  <span className="text-neutral-900">SMS Messaging</span>
                </div>
              </label>
              <label className="flex items-center space-x-2 border p-3 rounded-md w-full hover:bg-neutral-50 transition-colors cursor-pointer">
                <Checkbox
                  checked={formData.capabilities.includes("voice")}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    toggleCapability("voice", e.target.checked)
                  }
                />
                <div className="flex items-center">
                  <PhoneIcon className="h-4 w-4 mr-2 text-neutral-900" />
                  <span className="text-neutral-900">Voice Calls</span>
                </div>
              </label>
            </div>
          </div>

          {/* Placeholder for Tools - can be expanded later */}
          <div className="space-y-3 opacity-50 pointer-events-none">
            <Label>Tools (Coming Soon)</Label>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-2 border p-3 rounded-md">
                <Checkbox id="tool-calendly" disabled />
                <Label htmlFor="tool-calendly">Calendly Integration</Label>
              </div>
              <div className="flex items-center space-x-2 border p-3 rounded-md">
                <Checkbox id="tool-zapier" disabled />
                <Label htmlFor="tool-zapier">Zapier Webhooks</Label>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending && <Spinner size="sm" className="mr-2" />}
              {isEditing ? "Save Changes" : "Create Agent"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
