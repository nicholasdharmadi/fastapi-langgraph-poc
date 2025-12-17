import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { campaignsApi, leadsApi } from "../../services/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "../ui/dialog";
import { Button } from "../ui/button";
import { StepDetails } from "./StepDetails";
import { StepAgentSelection } from "./StepAgentSelection";
import { StepAudience } from "./StepAudience";
import { Spinner } from "../ui/spinner";

interface CampaignWizardProps {
  onClose: () => void;
  totalLeads?: number; // Optional now since unused
}

export function CampaignWizard({ onClose }: CampaignWizardProps) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    agent_id: null as number | null,
    lead_ids: [] as number[],
    phone_numbers: [] as string[],
    csvFile: null as File | null,
    // Legacy fields (hidden but required by backend if agent_id not supported yet)
    agent_type: "sms",
    sms_system_prompt: "",
    sms_temperature: 70,
  });
  const [uploadStatus, setUploadStatus] = useState("");

  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (data: any) => campaignsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      onClose();
    },
  });

  const handleNext = () => {
    if (step < 3) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = async () => {
    try {
      if (formData.csvFile) {
        setUploadStatus("Uploading leads...");
        await leadsApi.upload(formData.csvFile);
        setUploadStatus("Leads uploaded. Creating campaign...");
      }

      const payload = {
        name: formData.name,
        description: formData.description,
        agent_id: formData.agent_id,
        lead_ids: formData.lead_ids,
        phone_numbers: formData.phone_numbers,
        // Defaults
        agent_type: "sms",
        sms_temperature: 70,
      };

      createMutation.mutate(payload);
    } catch (error) {
      console.error("Error creating campaign:", error);
      setUploadStatus("Error creating campaign");
    }
  };

  const isStepValid = () => {
    if (step === 1) return formData.name.length > 0;
    if (step === 2) return formData.agent_id !== null;
    if (step === 3)
      return (
        formData.lead_ids.length > 0 ||
        formData.phone_numbers.length > 0 ||
        formData.csvFile !== null
      );
    return false;
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto flex flex-col">
        <DialogHeader>
          <DialogTitle>Create New Campaign</DialogTitle>
          <DialogDescription>
            Step {step} of 3:{" "}
            {step === 1
              ? "Campaign Details"
              : step === 2
              ? "Select Agent"
              : "Target Audience"}
          </DialogDescription>
        </DialogHeader>

        {/* Progress Bar */}
        <div className="w-full bg-neutral-100 h-2 rounded-full mb-6 overflow-hidden">
          <div
            className="bg-neutral-900 h-full transition-all duration-300 ease-in-out"
            style={{ width: `${(step / 3) * 100}%` }}
          />
        </div>

        <div className="flex-1 overflow-y-auto py-2">
          {step === 1 && (
            <StepDetails
              data={formData}
              onChange={(data) => setFormData({ ...formData, ...data })}
            />
          )}
          {step === 2 && (
            <StepAgentSelection
              selectedAgentId={formData.agent_id}
              onSelect={(id) => setFormData({ ...formData, agent_id: id })}
            />
          )}
          {step === 3 && (
            <StepAudience
              data={formData}
              onChange={(data) => setFormData({ ...formData, ...data })}
            />
          )}
        </div>

        <DialogFooter className="mt-6 border-t pt-4">
          <div className="flex justify-between w-full items-center">
            <div className="text-sm text-neutral-500">
              {uploadStatus && (
                <span className="flex items-center gap-2">
                  <Spinner size="sm" /> {uploadStatus}
                </span>
              )}
            </div>
            <div className="flex gap-2">
              {step > 1 && (
                <Button variant="outline" onClick={handleBack}>
                  Back
                </Button>
              )}
              {step < 3 ? (
                <Button onClick={handleNext} disabled={!isStepValid()}>
                  Next
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  disabled={!isStepValid() || createMutation.isPending}
                >
                  {createMutation.isPending ? "Creating..." : "Launch Campaign"}
                </Button>
              )}
            </div>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
