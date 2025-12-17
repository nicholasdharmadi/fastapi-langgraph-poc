import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { leadsApi } from "../../services/api";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { Checkbox } from "../ui/checkbox";
import { Spinner } from "../ui/spinner";
import {
  UserGroupIcon,
  CloudArrowUpIcon,
  PencilSquareIcon,
} from "@heroicons/react/24/outline";

interface StepAudienceProps {
  data: {
    lead_ids: number[];
    phone_numbers: string[];
    csvFile: File | null;
  };
  onChange: (data: any) => void;
}

export function StepAudience({ data, onChange }: StepAudienceProps) {
  const [activeTab, setActiveTab] = useState("existing");
  const [manualText, setManualText] = useState(data.phone_numbers.join("\n"));

  const { data: leads, isLoading } = useQuery({
    queryKey: ["leads"],
    queryFn: () => leadsApi.list().then((res) => res.data),
  });

  const handleManualChange = (text: string) => {
    setManualText(text);
    const phones = text
      .split("\n")
      .map((p) => p.trim())
      .filter((p) => p);
    onChange({ ...data, phone_numbers: phones });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onChange({ ...data, csvFile: file });
    }
  };

  const toggleLead = (id: number) => {
    const newIds = data.lead_ids.includes(id)
      ? data.lead_ids.filter((lid) => lid !== id)
      : [...data.lead_ids, id];
    onChange({ ...data, lead_ids: newIds });
  };

  const toggleAllLeads = () => {
    if (!leads) return;
    if (data.lead_ids.length === leads.length) {
      onChange({ ...data, lead_ids: [] });
    } else {
      onChange({ ...data, lead_ids: leads.map((l) => l.id) });
    }
  };

  return (
    <div className="space-y-6 py-4">
      <div className="flex space-x-1 rounded-xl bg-neutral-100 p-1">
        <button
          className={`w-full rounded-lg py-2.5 text-sm font-medium leading-5 ring-white ring-opacity-60 ring-offset-2 ring-offset-neutral-400 focus:outline-none focus:ring-2 ${
            activeTab === "existing"
              ? "bg-white shadow text-neutral-900"
              : "text-neutral-500 hover:bg-white/[0.12] hover:text-neutral-900"
          }`}
          onClick={() => setActiveTab("existing")}
        >
          <div className="flex items-center justify-center gap-2">
            <UserGroupIcon className="h-4 w-4" />
            Existing Leads
          </div>
        </button>
        <button
          className={`w-full rounded-lg py-2.5 text-sm font-medium leading-5 ring-white ring-opacity-60 ring-offset-2 ring-offset-neutral-400 focus:outline-none focus:ring-2 ${
            activeTab === "upload"
              ? "bg-white shadow text-neutral-900"
              : "text-neutral-500 hover:bg-white/[0.12] hover:text-neutral-900"
          }`}
          onClick={() => setActiveTab("upload")}
        >
          <div className="flex items-center justify-center gap-2">
            <CloudArrowUpIcon className="h-4 w-4" />
            Upload CSV
          </div>
        </button>
        <button
          className={`w-full rounded-lg py-2.5 text-sm font-medium leading-5 ring-white ring-opacity-60 ring-offset-2 ring-offset-neutral-400 focus:outline-none focus:ring-2 ${
            activeTab === "manual"
              ? "bg-white shadow text-neutral-900"
              : "text-neutral-500 hover:bg-white/[0.12] hover:text-neutral-900"
          }`}
          onClick={() => setActiveTab("manual")}
        >
          <div className="flex items-center justify-center gap-2">
            <PencilSquareIcon className="h-4 w-4" />
            Manual Entry
          </div>
        </button>
      </div>

      <div className="mt-4">
        {activeTab === "existing" && (
          <div className="space-y-4">
            {isLoading ? (
              <Spinner />
            ) : (
              <div className="border rounded-md overflow-hidden">
                <div className="bg-neutral-50 px-4 py-2 border-b flex items-center gap-3">
                  <Checkbox
                    checked={
                      leads &&
                      leads.length > 0 &&
                      data.lead_ids.length === leads.length
                    }
                    onChange={toggleAllLeads}
                  />
                  <span className="text-sm font-medium text-neutral-700">
                    Select All ({leads?.length || 0})
                  </span>
                </div>
                <div className="max-h-[300px] overflow-y-auto p-2 space-y-1">
                  {leads?.map((lead) => (
                    <div
                      key={lead.id}
                      className="flex items-center gap-3 p-2 hover:bg-neutral-50 rounded-md"
                    >
                      <Checkbox
                        checked={data.lead_ids.includes(lead.id)}
                        onChange={() => toggleLead(lead.id)}
                      />
                      <div className="flex-1">
                        <div className="font-medium text-sm">{lead.name}</div>
                        <div className="text-xs text-neutral-500">
                          {lead.phone} • {lead.email || "No email"}
                        </div>
                      </div>
                    </div>
                  ))}
                  {(!leads || leads.length === 0) && (
                    <div className="p-8 text-center text-neutral-500 text-sm">
                      No existing leads found.
                    </div>
                  )}
                </div>
              </div>
            )}
            <p className="text-xs text-neutral-500">
              Selected: {data.lead_ids.length} leads
            </p>
          </div>
        )}

        {activeTab === "upload" && (
          <div className="space-y-4 border-2 border-dashed border-neutral-200 rounded-lg p-8 text-center">
            <CloudArrowUpIcon className="h-12 w-12 text-neutral-300 mx-auto" />
            <div>
              <Label htmlFor="csv-upload" className="cursor-pointer">
                <span className="mt-2 block text-sm font-semibold text-neutral-900">
                  {data.csvFile ? data.csvFile.name : "Upload a CSV file"}
                </span>
                <input
                  id="csv-upload"
                  type="file"
                  accept=".csv"
                  className="sr-only"
                  onChange={handleFileChange}
                />
              </Label>
              <p className="mt-1 text-xs text-neutral-500">
                CSV should contain 'name' and 'phone' columns
              </p>
            </div>
            {data.csvFile && (
              <div className="mt-4 p-2 bg-neutral-100 text-neutral-900 text-sm rounded-md inline-block">
                File selected ready for upload
              </div>
            )}
          </div>
        )}

        {activeTab === "manual" && (
          <div className="space-y-2">
            <Label>Enter Phone Numbers</Label>
            <Textarea
              value={manualText}
              onChange={(e) => handleManualChange(e.target.value)}
              placeholder="+1234567890&#10;+1987654321"
              className="font-mono min-h-[200px]"
            />
            <p className="text-xs text-neutral-500">
              One phone number per line. Leads will be created automatically.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
