import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { campaignsApi, leadsApi, workflowsApi } from "../../services/api";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { Spinner } from "../ui/spinner";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import {
  CheckIcon,
  ChevronRightIcon,
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  RocketLaunchIcon,
  DocumentTextIcon,
} from "@heroicons/react/24/solid";

interface CampaignWizardProps {
  onClose: () => void;
  totalLeads: number;
}

const STEPS = [
  { id: 1, name: "Identity", icon: DocumentTextIcon },
  { id: 2, name: "Strategy", icon: ChatBubbleLeftRightIcon },
  { id: 3, name: "Audience", icon: UserGroupIcon },
  { id: 4, name: "Review", icon: RocketLaunchIcon },
];

export function CampaignWizard({ onClose, totalLeads }: CampaignWizardProps) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    agent_type: "sms" as "sms" | "voice" | "both",
    sms_system_prompt:
      "You are a helpful sales assistant. Generate a friendly, professional SMS message.",
    sms_temperature: 70,
    lead_count: 0,
    workflow_id: null as number | null,
    workflow_config: null as any,
    phone_numbers: [] as string[],
    lead_source: "random" as "random" | "csv" | "manual",
  });

  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [manualPhones, setManualPhones] = useState("");
  const [uploadStatus, setUploadStatus] = useState("");

  const queryClient = useQueryClient();

  const { data: workflows } = useQuery({
    queryKey: ["workflows"],
    queryFn: () => workflowsApi.list().then((res) => res.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: typeof formData) => campaignsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      onClose();
    },
  });

  const handleNext = async () => {
    if (step === 4) {
      // Submit
      try {
        if (formData.lead_source === "csv" && csvFile) {
          setUploadStatus("Uploading leads...");
          await leadsApi.upload(csvFile);
          setUploadStatus("Leads uploaded.");
        }

        const phones = manualPhones
          .split("\n")
          .map((p) => p.trim())
          .filter((p) => p);

        createMutation.mutate({
          ...formData,
          phone_numbers: phones,
        });
      } catch (error) {
        console.error("Error:", error);
        setUploadStatus("Error creating campaign");
      }
    } else {
      setStep(step + 1);
    }
  };

  const isStepValid = () => {
    switch (step) {
      case 1:
        return formData.name.length > 0;
      case 2:
        return true; // Defaults are set
      case 3:
        if (formData.lead_source === "random") return formData.lead_count > 0;
        if (formData.lead_source === "csv") return !!csvFile;
        if (formData.lead_source === "manual") return manualPhones.length > 0;
        return false;
      default:
        return true;
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl h-[80vh] flex flex-col p-0 overflow-hidden">
        <div className="flex h-full">
          {/* Sidebar */}
          <div className="w-64 bg-neutral-50 border-r p-6 flex flex-col">
            <div className="mb-8">
              <h2 className="text-lg font-bold">New Campaign</h2>
              <p className="text-sm text-neutral-500">Create your outreach</p>
            </div>
            <nav className="space-y-1">
              {STEPS.map((s) => {
                const Icon = s.icon;
                const isActive = step === s.id;
                const isCompleted = step > s.id;
                return (
                  <div
                    key={s.id}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? "bg-white shadow text-neutral-900"
                        : isCompleted
                        ? "text-neutral-500"
                        : "text-neutral-400"
                    }`}
                  >
                    <div
                      className={`h-6 w-6 rounded-full flex items-center justify-center border ${
                        isActive
                          ? "border-neutral-900 bg-neutral-900 text-white"
                          : isCompleted
                          ? "border-green-600 bg-green-600 text-white"
                          : "border-neutral-200"
                      }`}
                    >
                      {isCompleted ? (
                        <CheckIcon className="h-3 w-3" />
                      ) : (
                        <Icon className="h-3 w-3" />
                      )}
                    </div>
                    {s.name}
                  </div>
                );
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 flex flex-col">
            <DialogHeader className="p-6 border-b">
              <DialogTitle>{STEPS[step - 1].name}</DialogTitle>
            </DialogHeader>

            <div className="flex-1 p-6 overflow-y-auto">
              {step === 1 && (
                <div className="space-y-4 max-w-md">
                  <div className="space-y-2">
                    <Label htmlFor="name">Campaign Name</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) =>
                        setFormData({ ...formData, name: e.target.value })
                      }
                      placeholder="e.g., Q4 Sales Outreach"
                      autoFocus
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          description: e.target.value,
                        })
                      }
                      placeholder="What is the goal of this campaign?"
                    />
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div
                      className={`border rounded-xl p-4 cursor-pointer transition-all ${
                        !formData.workflow_id
                          ? "ring-2 ring-neutral-900 border-transparent bg-neutral-50"
                          : "hover:border-neutral-300"
                      }`}
                      onClick={() =>
                        setFormData({ ...formData, workflow_id: null })
                      }
                    >
                      <div className="font-semibold mb-1">Simple Blast</div>
                      <p className="text-sm text-neutral-500">
                        Send a single message using a system prompt. Best for
                        announcements.
                      </p>
                    </div>
                    <div
                      className={`border rounded-xl p-4 cursor-pointer transition-all ${
                        formData.workflow_id
                          ? "ring-2 ring-neutral-900 border-transparent bg-neutral-50"
                          : "hover:border-neutral-300"
                      }`}
                      onClick={() =>
                        workflows &&
                        workflows.length > 0 &&
                        setFormData({
                          ...formData,
                          workflow_id: workflows[0].id,
                          workflow_config: workflows[0].config,
                        })
                      }
                    >
                      <div className="font-semibold mb-1">Smart Workflow</div>
                      <p className="text-sm text-neutral-500">
                        Use a multi-step LangGraph workflow for complex
                        interactions.
                      </p>
                    </div>
                  </div>

                  {!formData.workflow_id ? (
                    <div className="space-y-4 animate-in fade-in slide-in-from-top-2">
                      <div className="space-y-2">
                        <Label>System Prompt</Label>
                        <Textarea
                          value={formData.sms_system_prompt}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              sms_system_prompt: e.target.value,
                            })
                          }
                          rows={4}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>
                          Temperature: {formData.sms_temperature / 100}
                        </Label>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={formData.sms_temperature}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              sms_temperature: parseInt(e.target.value),
                            })
                          }
                          className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="grid gap-4 grid-cols-2 animate-in fade-in slide-in-from-top-2">
                      {workflows?.map((w) => (
                        <div
                          key={w.id}
                          className={`border rounded-lg p-4 cursor-pointer ${
                            formData.workflow_id === w.id
                              ? "bg-blue-50 border-blue-500"
                              : "hover:bg-neutral-50"
                          }`}
                          onClick={() =>
                            setFormData({
                              ...formData,
                              workflow_id: w.id,
                              workflow_config: w.config,
                            })
                          }
                        >
                          <div className="font-medium">{w.name}</div>
                          <div className="text-xs text-neutral-500 mt-1">
                            {w.description}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {step === 3 && (
                <div className="space-y-6">
                  <div className="flex gap-4 border-b">
                    {(["random", "csv", "manual"] as const).map((source) => (
                      <button
                        key={source}
                        className={`pb-2 text-sm font-medium capitalize ${
                          formData.lead_source === source
                            ? "border-b-2 border-neutral-900 text-neutral-900"
                            : "text-neutral-500"
                        }`}
                        onClick={() =>
                          setFormData({ ...formData, lead_source: source })
                        }
                      >
                        {source} Import
                      </button>
                    ))}
                  </div>

                  <div className="pt-4">
                    {formData.lead_source === "random" && (
                      <div className="space-y-2 max-w-xs">
                        <Label>Number of Leads</Label>
                        <Input
                          type="number"
                          min="1"
                          max={totalLeads}
                          value={formData.lead_count}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              lead_count: parseInt(e.target.value),
                            })
                          }
                        />
                        <p className="text-xs text-neutral-500">
                          Available leads: {totalLeads}
                        </p>
                      </div>
                    )}

                    {formData.lead_source === "csv" && (
                      <div className="space-y-4">
                        <div className="border-2 border-dashed rounded-lg p-8 text-center hover:bg-neutral-50 transition-colors">
                          <input
                            type="file"
                            id="csv"
                            className="hidden"
                            accept=".csv"
                            onChange={(e) =>
                              setCsvFile(e.target.files?.[0] || null)
                            }
                          />
                          <label htmlFor="csv" className="cursor-pointer">
                            <DocumentTextIcon className="h-8 w-8 mx-auto text-neutral-400 mb-2" />
                            <span className="text-sm font-medium">
                              {csvFile ? csvFile.name : "Click to upload CSV"}
                            </span>
                          </label>
                        </div>
                        <p className="text-xs text-neutral-500">
                          Required columns: name, phone
                        </p>
                      </div>
                    )}

                    {formData.lead_source === "manual" && (
                      <div className="space-y-2">
                        <Label>Phone Numbers (one per line)</Label>
                        <Textarea
                          value={manualPhones}
                          onChange={(e) => setManualPhones(e.target.value)}
                          rows={6}
                          placeholder="+1234567890"
                        />
                      </div>
                    )}
                  </div>
                </div>
              )}

              {step === 4 && (
                <div className="space-y-6">
                  <div className="bg-neutral-50 rounded-lg p-6 space-y-4">
                    <div className="flex justify-between border-b pb-4">
                      <div>
                        <div className="text-sm text-neutral-500">Campaign</div>
                        <div className="font-semibold text-lg">
                          {formData.name}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-neutral-500">Strategy</div>
                        <div className="font-medium">
                          {formData.workflow_id
                            ? "Smart Workflow"
                            : "Simple Blast"}
                        </div>
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-neutral-500 mb-1">
                        Audience
                      </div>
                      <div className="font-medium flex items-center gap-2">
                        <UserGroupIcon className="h-4 w-4" />
                        {formData.lead_source === "random"
                          ? `${formData.lead_count} Random Leads`
                          : formData.lead_source === "csv"
                          ? `CSV Upload: ${csvFile?.name}`
                          : "Manual Entry"}
                      </div>
                    </div>
                  </div>

                  {uploadStatus && (
                    <div className="text-sm text-blue-600 animate-pulse">
                      {uploadStatus}
                    </div>
                  )}
                </div>
              )}
            </div>

            <DialogFooter className="p-6 border-t bg-neutral-50">
              <Button variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button
                onClick={handleNext}
                disabled={!isStepValid() || createMutation.isPending}
              >
                {createMutation.isPending && (
                  <Spinner size="sm" className="mr-2" />
                )}
                {step === 4 ? "Launch Campaign" : "Next Step"}
                {step !== 4 && <ChevronRightIcon className="ml-2 h-4 w-4" />}
              </Button>
            </DialogFooter>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
