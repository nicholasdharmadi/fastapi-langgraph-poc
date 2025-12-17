import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  CloudArrowUpIcon,
  DocumentTextIcon,
  SparklesIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  MicrophoneIcon,
  ChatBubbleLeftRightIcon,
} from "@heroicons/react/24/outline";
import { cn } from "../lib/utils";
import { PromptBuilderChat } from "../components/prompt-builder/PromptBuilderChat";

interface Recording {
  id: number;
  filename: string;
  file_size: number;
  duration: number | null;
  status: "uploaded" | "transcribing" | "analyzing" | "completed" | "failed";
  created_at: string;
  error_message: string | null;
}

interface RecordingDetail extends Recording {
  transcript: {
    full_text: string;
    speaker_segments: any[];
  } | null;
  analysis: {
    tonality_description: string;
    communication_style: any;
    hooks: any[];
    objections: any[];
    key_phrases: string[];
    voice_profile: any;
  } | null;
  prompts: GeneratedPrompt[];
}

interface GeneratedPrompt {
  id: number;
  recording_id: number;
  prompt_text: string;
  version: number;
  voice_settings: any;
  is_active: boolean;
  created_at: string;
}

const API_BASE = "/api";

export default function PromptBuilderPage() {
  const [mode, setMode] = useState<"recording" | "chat">("recording");
  const [selectedRecording, setSelectedRecording] = useState<number | null>(
    null
  );
  const [generatedPrompt, setGeneratedPrompt] = useState<any>(null);
  const [draftPrompt, setDraftPrompt] = useState<string>("");
  const [uploading, setUploading] = useState(false);
  const queryClient = useQueryClient();

  // Fetch recordings
  const { data: recordings = [], isLoading } = useQuery<Recording[]>({
    queryKey: ["recordings"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/recordings`);
      if (!res.ok) throw new Error("Failed to fetch recordings");
      return res.json();
    },
    refetchInterval: 5000,
    enabled: mode === "recording",
  });

  // Fetch selected recording details
  const { data: recordingDetail } = useQuery<RecordingDetail>({
    queryKey: ["recording", selectedRecording],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/recordings/${selectedRecording}`);
      if (!res.ok) throw new Error("Failed to fetch recording");
      return res.json();
    },
    enabled: !!selectedRecording && mode === "recording",
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/recordings/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recordings"] });
      setUploading(false);
    },
  });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    uploadMutation.mutate(file);
  };

  const getStatusIcon = (status: Recording["status"]) => {
    switch (status) {
      case "completed":
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case "failed":
        return <XCircleIcon className="h-5 w-5 text-red-600" />;
      case "transcribing":
      case "analyzing":
        return <ClockIcon className="h-5 w-5 text-blue-600 animate-spin" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: Recording["status"]) => {
    const map = {
      uploaded: "Queued",
      transcribing: "Transcribing...",
      analyzing: "Analyzing...",
      completed: "Ready",
      failed: "Failed",
    };
    return map[status];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 flex items-center gap-3">
            Prompt Builder
          </h1>
          <p className="mt-2 text-neutral-600">
            Generate AI agent prompts from recordings or interactive chat
          </p>
        </div>

        {/* Mode Toggle */}
        <div className="flex bg-neutral-100 p-1 rounded-lg">
          <button
            onClick={() => setMode("recording")}
            className={cn(
              "px-4 py-2 rounded-md text-sm font-medium transition-all",
              mode === "recording"
                ? "bg-white shadow text-blue-600"
                : "text-neutral-600 hover:text-neutral-900"
            )}
          >
            <div className="flex items-center gap-2">
              <CloudArrowUpIcon className="h-4 w-4" />
              From Recording
            </div>
          </button>
          <button
            onClick={() => setMode("chat")}
            className={cn(
              "px-4 py-2 rounded-md text-sm font-medium transition-all",
              mode === "chat"
                ? "bg-white shadow text-indigo-600"
                : "text-neutral-600 hover:text-neutral-900"
            )}
          >
            <div className="flex items-center gap-2">
              <ChatBubbleLeftRightIcon className="h-4 w-4" />
              Interactive Chat
            </div>
          </button>
        </div>
      </div>

      {mode === "recording" ? (
        <>
          <div className="flex justify-end">
            <label className="cursor-pointer">
              <input
                type="file"
                accept="audio/*"
                className="hidden"
                onChange={handleFileUpload}
                disabled={uploading}
              />
              <div
                className={cn(
                  "inline-flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all",
                  uploading
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl"
                )}
              >
                <CloudArrowUpIcon className="h-5 w-5" />
                {uploading ? "Uploading..." : "Upload Recording"}
              </div>
            </label>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recordings List */}
            <div className="lg:col-span-1 bg-white rounded-lg shadow-sm border border-neutral-200">
              <div className="p-4 border-b border-neutral-200">
                <h2 className="font-semibold text-neutral-900">Recordings</h2>
              </div>
              <div className="divide-y divide-neutral-200 max-h-[600px] overflow-y-auto">
                {isLoading ? (
                  <div className="p-8 text-center text-neutral-500">
                    Loading...
                  </div>
                ) : recordings.length === 0 ? (
                  <div className="p-8 text-center text-neutral-500">
                    No recordings yet. Upload one to get started!
                  </div>
                ) : (
                  recordings.map((recording) => (
                    <button
                      key={recording.id}
                      onClick={() => setSelectedRecording(recording.id)}
                      className={cn(
                        "w-full p-4 text-left hover:bg-neutral-50 transition-colors",
                        selectedRecording === recording.id && "bg-blue-50"
                      )}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-neutral-900 truncate">
                            {recording.filename}
                          </p>
                          <p className="text-sm text-neutral-500 mt-1">
                            {new Date(
                              recording.created_at
                            ).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(recording.status)}
                        </div>
                      </div>
                      <div className="mt-2 flex items-center gap-2">
                        <span className="text-xs px-2 py-1 rounded-full bg-neutral-100 text-neutral-600">
                          {getStatusText(recording.status)}
                        </span>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Detail View */}
            <div className="lg:col-span-2 space-y-6">
              {!selectedRecording ? (
                <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-12 text-center">
                  <DocumentTextIcon className="h-16 w-16 text-neutral-300 mx-auto mb-4" />
                  <p className="text-neutral-500">
                    Select a recording to view details and generated prompts
                  </p>
                </div>
              ) : !recordingDetail ? (
                <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-12 text-center">
                  <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto"></div>
                  <p className="text-neutral-500 mt-4">Loading...</p>
                </div>
              ) : (
                <>
                  {/* Analysis Results */}
                  {recordingDetail.analysis && (
                    <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
                      <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                        <SparklesIcon className="h-5 w-5 text-purple-600" />
                        Analysis Results
                      </h3>

                      <div className="space-y-4">
                        {/* Tonality */}
                        <div>
                          <h4 className="font-medium text-neutral-700 mb-2">
                            Tonality
                          </h4>
                          <p className="text-neutral-600">
                            {recordingDetail.analysis.tonality_description}
                          </p>
                        </div>

                        {/* Communication Style */}
                        {recordingDetail.analysis.communication_style && (
                          <div>
                            <h4 className="font-medium text-neutral-700 mb-2">
                              Communication Style
                            </h4>
                            <div className="flex gap-2 flex-wrap">
                              {Object.entries(
                                recordingDetail.analysis.communication_style
                              ).map(([key, value]) => (
                                <span
                                  key={key}
                                  className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                                >
                                  {key}: {value as string}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Key Phrases */}
                        {recordingDetail.analysis.key_phrases?.length > 0 && (
                          <div>
                            <h4 className="font-medium text-neutral-700 mb-2">
                              Key Phrases
                            </h4>
                            <div className="flex gap-2 flex-wrap">
                              {recordingDetail.analysis.key_phrases.map(
                                (phrase, idx) => (
                                  <span
                                    key={idx}
                                    className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                                  >
                                    {phrase}
                                  </span>
                                )
                              )}
                            </div>
                          </div>
                        )}

                        {/* Hooks */}
                        {recordingDetail.analysis.hooks?.length > 0 && (
                          <div>
                            <h4 className="font-medium text-neutral-700 mb-2">
                              Effective Hooks
                            </h4>
                            <ul className="space-y-2">
                              {recordingDetail.analysis.hooks.map(
                                (hook: any, idx: number) => (
                                  <li
                                    key={idx}
                                    className="p-3 bg-neutral-50 rounded-lg border border-neutral-200"
                                  >
                                    <p className="text-neutral-800">
                                      {hook.text}
                                    </p>
                                    {hook.effectiveness && (
                                      <span className="text-xs text-neutral-500 mt-1">
                                        Effectiveness: {hook.effectiveness}
                                      </span>
                                    )}
                                  </li>
                                )
                              )}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Generated Prompts */}
                  <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
                    <h3 className="text-lg font-semibold text-neutral-900 mb-4">
                      Generated Prompts
                    </h3>

                    {recordingDetail.prompts.length === 0 ? (
                      <p className="text-neutral-500 text-center py-8">
                        {recordingDetail.status === "completed"
                          ? "No prompts generated yet"
                          : "Processing... Prompts will appear when ready"}
                      </p>
                    ) : (
                      <div className="space-y-4">
                        {recordingDetail.prompts.map((prompt) => (
                          <div
                            key={prompt.id}
                            className={cn(
                              "p-4 rounded-lg border-2",
                              prompt.is_active
                                ? "border-blue-500 bg-blue-50"
                                : "border-neutral-200 bg-white"
                            )}
                          >
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-neutral-900">
                                  Version {prompt.version}
                                </span>
                                {prompt.is_active && (
                                  <span className="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">
                                    Active
                                  </span>
                                )}
                              </div>
                              <span className="text-sm text-neutral-500">
                                {new Date(
                                  prompt.created_at
                                ).toLocaleDateString()}
                              </span>
                            </div>
                            <div className="bg-neutral-900 text-neutral-100 p-4 rounded-lg font-mono text-sm whitespace-pre-wrap max-h-96 overflow-y-auto">
                              {prompt.prompt_text}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </>
      ) : (
        // Chat Mode
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-200px)]">
          <PromptBuilderChat
            onPromptGenerated={setGeneratedPrompt}
            onDraftUpdate={setDraftPrompt}
          />

          {generatedPrompt ? (
            <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6 flex flex-col h-[600px]">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                <CheckCircleIcon className="h-5 w-5 text-green-600" />
                Generated Prompt
              </h3>
              <div className="flex-1 overflow-y-auto bg-neutral-900 text-neutral-100 p-4 rounded-lg font-mono text-sm whitespace-pre-wrap">
                {generatedPrompt.prompt_text}
              </div>
            </div>
          ) : draftPrompt ? (
            <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6 flex flex-col h-[600px]">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                <DocumentTextIcon className="h-5 w-5 text-blue-600" />
                Live Prompt Draft
              </h3>
              <div className="flex-1 overflow-y-auto bg-neutral-50 text-neutral-800 p-4 rounded-lg font-mono text-sm whitespace-pre-wrap border border-neutral-200">
                {draftPrompt}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-12 text-center flex flex-col items-center justify-center h-[600px]">
              <SparklesIcon className="h-16 w-16 text-neutral-300 mb-4" />
              <p className="text-neutral-500">
                Chat with the AI to build your prompt.
                <br />
                The generated prompt will appear here.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
