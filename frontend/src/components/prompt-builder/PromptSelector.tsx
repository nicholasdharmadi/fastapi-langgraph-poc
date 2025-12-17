import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import {
  DocumentTextIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/solid";
import { cn } from "../../lib/utils";
import { formatDate } from "../../lib/utils";

interface SavedPrompt {
  id: number;
  name: string | null;
  prompt_text: string;
  source_type: string;
  created_at: string;
  is_active: boolean;
}

interface PromptSelectorProps {
  open: boolean;
  onClose: () => void;
  onSelect: (promptText: string) => void;
}

export function PromptSelector({
  open,
  onClose,
  onSelect,
}: PromptSelectorProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const { data: prompts, isLoading } = useQuery<SavedPrompt[]>({
    queryKey: ["saved-prompts"],
    queryFn: async () => {
      const res = await fetch("/api/prompts/library");
      if (!res.ok) throw new Error("Failed to fetch prompts");
      return res.json();
    },
    enabled: open,
  });

  const filteredPrompts = prompts?.filter(
    (p) =>
      p.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.prompt_text.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSelect = () => {
    const selected = prompts?.find((p) => p.id === selectedId);
    if (selected) {
      onSelect(selected.prompt_text);
      onClose();
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Select a Saved Prompt</DialogTitle>
          <DialogDescription>
            Choose from your previously generated prompts
          </DialogDescription>
        </DialogHeader>

        <div className="relative mb-4">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
          <Input
            placeholder="Search prompts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        <div className="flex-1 overflow-y-auto space-y-3">
          {isLoading ? (
            <div className="text-center py-12 text-neutral-500">
              Loading prompts...
            </div>
          ) : filteredPrompts && filteredPrompts.length > 0 ? (
            filteredPrompts.map((prompt) => (
              <div
                key={prompt.id}
                className={cn(
                  "border rounded-lg p-4 cursor-pointer transition-all hover:border-neutral-400",
                  selectedId === prompt.id
                    ? "border-blue-500 bg-blue-50 ring-1 ring-blue-500"
                    : "border-neutral-200"
                )}
                onClick={() => setSelectedId(prompt.id)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <DocumentTextIcon className="h-5 w-5 text-blue-600" />
                    <h3 className="font-medium text-neutral-900">
                      {prompt.name || `Prompt #${prompt.id}`}
                    </h3>
                    <span
                      className={cn(
                        "px-2 py-0.5 rounded-full text-xs font-medium",
                        prompt.source_type === "CHAT"
                          ? "bg-indigo-100 text-indigo-700"
                          : "bg-green-100 text-green-700"
                      )}
                    >
                      {prompt.source_type === "CHAT"
                        ? "Interactive"
                        : "Recording"}
                    </span>
                  </div>
                  {selectedId === prompt.id && (
                    <CheckCircleIcon className="h-5 w-5 text-blue-600" />
                  )}
                </div>
                <p className="text-sm text-neutral-600 line-clamp-3 font-mono bg-neutral-50 p-2 rounded">
                  {prompt.prompt_text}
                </p>
                <p className="text-xs text-neutral-400 mt-2">
                  Created {formatDate(prompt.created_at)}
                </p>
              </div>
            ))
          ) : (
            <div className="text-center py-12 text-neutral-500">
              {searchQuery
                ? "No prompts match your search"
                : "No saved prompts yet"}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSelect} disabled={!selectedId}>
            Use Selected Prompt
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
