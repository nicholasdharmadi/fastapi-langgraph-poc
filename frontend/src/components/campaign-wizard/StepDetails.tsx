import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";

interface StepDetailsProps {
  data: {
    name: string;
    description: string;
  };
  onChange: (data: any) => void;
}

export function StepDetails({ data, onChange }: StepDetailsProps) {
  return (
    <div className="space-y-6 py-4">
      <div className="space-y-2">
        <Label htmlFor="name">Campaign Name</Label>
        <Input
          id="name"
          value={data.name}
          onChange={(e) => onChange({ ...data, name: e.target.value })}
          placeholder="e.g., Q4 Outreach"
          autoFocus
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={data.description}
          onChange={(e) => onChange({ ...data, description: e.target.value })}
          placeholder="What is the goal of this campaign?"
        />
      </div>
    </div>
  );
}
