import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Spinner } from "./ui/spinner";
import { formatDate } from "../lib/utils";

interface ConversationMessage {
  id: number;
  campaign_lead_id: number;
  role: string;
  content: string;
  message_metadata?: {
    node?: string;
    step?: string;
    cost?: number;
  };
  created_at: string;
}

interface ConversationViewerProps {
  campaignLeadId: number;
  traceUrl?: string;
}

export default function ConversationViewer({
  campaignLeadId,
  traceUrl,
}: ConversationViewerProps) {
  const { data: messages, isLoading } = useQuery<ConversationMessage[]>({
    queryKey: ["conversations", campaignLeadId],
    queryFn: () =>
      api
        .get(`/api/conversations/campaign-lead/${campaignLeadId}`)
        .then((res) => res.data),
  });

  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <Spinner />
      </div>
    );
  }

  if (!messages || messages.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-neutral-500">
          No conversation history available
        </CardContent>
      </Card>
    );
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case "system":
        return "bg-blue-50 border-blue-200 text-blue-900";
      case "assistant":
        return "bg-green-50 border-green-200 text-green-900";
      case "user":
        return "bg-purple-50 border-purple-200 text-purple-900";
      default:
        return "bg-neutral-50 border-neutral-200 text-neutral-900";
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "system":
        return "⚙️";
      case "assistant":
        return "🤖";
      case "user":
        return "👤";
      default:
        return "💬";
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Conversation History</h3>
        {traceUrl && (
          <a
            href={traceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            <span>View in LangSmith</span>
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
        )}
      </div>

      <div className="space-y-3">
        {messages.map((message) => (
          <Card
            key={message.id}
            className={`border ${getRoleColor(message.role)}`}
          >
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{getRoleIcon(message.role)}</span>
                  <CardTitle className="text-sm font-medium capitalize">
                    {message.role}
                  </CardTitle>
                  {message.message_metadata?.node && (
                    <span className="text-xs px-2 py-0.5 bg-white rounded-full border">
                      {message.message_metadata.node}
                    </span>
                  )}
                </div>
                <span className="text-xs text-neutral-500">
                  {formatDate(message.created_at)}
                </span>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              {message.message_metadata?.cost && (
                <div className="mt-2 text-xs text-neutral-600">
                  Cost: ${message.message_metadata.cost.toFixed(4)}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="text-xs text-neutral-500 text-center pt-2">
        {messages.length} message{messages.length !== 1 ? "s" : ""} in
        conversation
      </div>
    </div>
  );
}
