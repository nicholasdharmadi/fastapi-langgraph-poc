import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import {
  ArrowLeftIcon,
  PaperAirplaneIcon,
  UserIcon,
  ComputerDesktopIcon,
} from "@heroicons/react/24/solid";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";
import { PageLoader } from "../components/PageLoader";

interface ConversationMessage {
  id: number;
  campaign_lead_id: number;
  role: string;
  content: string;
  message_metadata?: {
    manual?: boolean;
    node?: string;
    [key: string]: any;
  };
  created_at: string;
}

interface CampaignLead {
  id: number;
  campaign_id: number;
  lead_id: number;
  status: string;
  manual_mode: boolean;
  lead: {
    id: number;
    name: string;
    phone: string;
    email?: string;
  };
  campaign: {
    id: number;
    name: string;
  };
}

export default function ConversationDetailPage() {
  const { campaignLeadId } = useParams<{ campaignLeadId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [messageText, setMessageText] = useState("");

  // Fetch conversation messages
  const { data: messages, isLoading: messagesLoading } = useQuery({
    queryKey: ["conversation", campaignLeadId],
    queryFn: async () => {
      const response = await axios.get(
        `/api/conversations/campaign-lead/${campaignLeadId}`
      );
      return response.data as ConversationMessage[];
    },
    refetchInterval: 5000, // Poll every 5 seconds for new messages
  });

  // Fetch campaign lead details
  const { data: campaignLead, isLoading: leadLoading } = useQuery({
    queryKey: ["campaign-lead", campaignLeadId],
    queryFn: async () => {
      const response = await axios.get(`/api/campaign-leads/${campaignLeadId}`);
      return response.data as CampaignLead;
    },
  });

  // Toggle manual mode mutation
  const toggleManualMode = useMutation({
    mutationFn: async (manualMode: boolean) => {
      await axios.post(
        `/api/conversations/campaign-lead/${campaignLeadId}/toggle-manual-mode`,
        { manual_mode: manualMode }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["campaign-lead", campaignLeadId],
      });
    },
  });

  // Send manual message mutation
  const sendMessage = useMutation({
    mutationFn: async (message: string) => {
      await axios.post(
        `/api/conversations/campaign-lead/${campaignLeadId}/send-manual-message`,
        { message }
      );
    },
    onSuccess: () => {
      setMessageText("");
      queryClient.invalidateQueries({
        queryKey: ["conversation", campaignLeadId],
      });
    },
  });

  const handleSendMessage = () => {
    if (messageText.trim()) {
      sendMessage.mutate(messageText);
    }
  };

  const handleToggleManualMode = () => {
    if (campaignLead) {
      toggleManualMode.mutate(!campaignLead.manual_mode);
    }
  };

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    const messagesContainer = document.getElementById("messages-container");
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }, [messages]);

  if (messagesLoading || leadLoading) {
    return <PageLoader />;
  }

  if (!campaignLead) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-neutral-500">Conversation not found</p>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-neutral-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate(`/campaigns/${campaignLead.campaign_id}`)}
            >
              <ArrowLeftIcon className="h-4 w-4" />
              Back
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-neutral-900">
                {campaignLead.lead.name}
              </h1>
              <p className="text-sm text-neutral-500">
                {campaignLead.lead.phone} • Campaign:{" "}
                {campaignLead.campaign.name}
              </p>
            </div>
          </div>

          {/* Manual Mode Toggle */}
          <div className="flex items-center gap-3">
            <span className="text-sm text-neutral-600">
              {campaignLead.manual_mode ? "Manual Mode" : "AI Mode"}
            </span>
            <button
              onClick={handleToggleManualMode}
              disabled={toggleManualMode.isPending}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                campaignLead.manual_mode ? "bg-neutral-900" : "bg-neutral-300"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  campaignLead.manual_mode ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
            {campaignLead.manual_mode ? (
              <UserIcon className="h-5 w-5 text-neutral-900" />
            ) : (
              <ComputerDesktopIcon className="h-5 w-5 text-neutral-500" />
            )}
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div
        id="messages-container"
        className="flex-1 overflow-y-auto px-6 py-4 space-y-4"
      >
        {messages && messages.length > 0 ? (
          messages.map((message) => {
            const isUser = message.role === "user";
            const isManual = message.message_metadata?.manual === true;

            return (
              <div
                key={message.id}
                className={`flex ${isUser ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg px-4 py-2 ${
                    isUser
                      ? "bg-neutral-900 text-white"
                      : isManual
                      ? "bg-blue-100 text-neutral-900 border border-blue-300"
                      : "bg-white text-neutral-900 border border-neutral-200"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    {!isUser && (
                      <span className="text-xs font-medium">
                        {isManual ? "👤 You" : "🤖 AI"}
                      </span>
                    )}
                    <span className="text-xs opacity-70">
                      {new Date(message.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm whitespace-pre-wrap">
                    {message.content}
                  </p>
                </div>
              </div>
            );
          })
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-neutral-500">No messages yet</p>
          </div>
        )}
      </div>

      {/* Message Input - Only show in manual mode */}
      {campaignLead.manual_mode && (
        <div className="bg-white border-t px-6 py-4">
          <div className="flex gap-3">
            <Textarea
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 min-h-[60px] max-h-[120px]"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
            />
            <Button
              onClick={handleSendMessage}
              disabled={!messageText.trim() || sendMessage.isPending}
              className="self-end"
            >
              <PaperAirplaneIcon className="h-4 w-4" />
              Send
            </Button>
          </div>
          <p className="text-xs text-neutral-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      )}

      {!campaignLead.manual_mode && (
        <div className="bg-neutral-100 border-t px-6 py-4 text-center">
          <p className="text-sm text-neutral-600">
            AI Mode is active. Toggle to Manual Mode to send messages.
          </p>
        </div>
      )}
    </div>
  );
}
