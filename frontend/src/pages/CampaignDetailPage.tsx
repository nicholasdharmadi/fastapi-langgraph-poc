import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, Link, useNavigate } from "react-router-dom";
import { campaignsApi } from "../services/api";
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  PauseIcon,
  PlayIcon,
  ChatBubbleBottomCenterTextIcon,
} from "@heroicons/react/24/solid";
import { getStatusColor, getStatusText } from "../lib/utils";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { PageLoader } from "../components/PageLoader";
import { LiveActivityFeed } from "../components/campaigns/LiveActivityFeed";

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const campaignId = parseInt(id || "0");
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data: campaign, isLoading } = useQuery({
    queryKey: ["campaign", campaignId],
    queryFn: () => campaignsApi.get(campaignId).then((res) => res.data),
    refetchInterval: 2000, // Faster polling for live feel
  });

  const { data: logs } = useQuery({
    queryKey: ["campaign-logs", campaignId],
    queryFn: () => campaignsApi.getLogs(campaignId).then((res) => res.data),
    refetchInterval: 2000,
  });

  const pauseMutation = useMutation({
    mutationFn: () => campaignsApi.pause(campaignId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["campaign", campaignId] }),
  });

  const resumeMutation = useMutation({
    mutationFn: () => campaignsApi.resume(campaignId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["campaign", campaignId] }),
  });

  const startMutation = useMutation({
    mutationFn: () => campaignsApi.start(campaignId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["campaign", campaignId] }),
  });

  if (isLoading) {
    return <PageLoader />;
  }

  if (!campaign) {
    return <div className="text-center py-12">Campaign not found</div>;
  }

  const isProcessing = campaign.status === "processing";
  const isPaused = campaign.status === "paused";
  const isDraft = campaign.status === "draft" || campaign.status === "pending";

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0">
        <Link
          to="/campaigns"
          className="inline-flex items-center gap-1 text-sm text-neutral-600 hover:text-neutral-900 mb-4"
        >
          <ArrowLeftIcon className="h-4 w-4" />
          Back to Campaigns
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-neutral-900 flex items-center gap-3">
              {campaign.name}
              <span
                className={`px-3 py-1 text-sm font-medium text-white rounded-full ${getStatusColor(
                  campaign.status
                )}`}
              >
                {getStatusText(campaign.status)}
              </span>
            </h2>
            {campaign.description && (
              <p className="mt-1 text-neutral-600">{campaign.description}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {isDraft && (
              <Button
                onClick={() => startMutation.mutate()}
                disabled={startMutation.isPending}
                className="bg-green-600 hover:bg-green-700"
              >
                <PlayIcon className="h-4 w-4 mr-2" />
                Start Campaign
              </Button>
            )}
            {isProcessing && (
              <Button
                variant="secondary"
                onClick={() => pauseMutation.mutate()}
                disabled={pauseMutation.isPending}
              >
                <PauseIcon className="h-4 w-4 mr-2" />
                Pause
              </Button>
            )}
            {isPaused && (
              <Button
                onClick={() => resumeMutation.mutate()}
                disabled={resumeMutation.isPending}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <PlayIcon className="h-4 w-4 mr-2" />
                Resume
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Stats & Leads (2/3 width) */}
        <div className="lg:col-span-2 flex flex-col gap-6 overflow-hidden">
          {/* Stats Cards */}
          {campaign.stats && (
            <div className="grid gap-4 md:grid-cols-3 flex-shrink-0">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Completed
                  </CardTitle>
                  <CheckCircleIcon className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {campaign.stats.completed}
                    <span className="text-sm font-normal text-neutral-500 ml-2">
                      / {campaign.stats.total_leads}
                    </span>
                  </div>
                  <div className="w-full bg-neutral-100 h-1 mt-2 rounded-full overflow-hidden">
                    <div
                      className="bg-green-500 h-full transition-all duration-500"
                      style={{
                        width: `${
                          (campaign.stats.completed /
                            campaign.stats.total_leads) *
                          100
                        }%`,
                      }}
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Pending</CardTitle>
                  <ClockIcon className="h-4 w-4 text-neutral-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {campaign.stats.pending}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Failed</CardTitle>
                  <XCircleIcon className="h-4 w-4 text-red-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {campaign.stats.failed}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Leads Table */}
          <Card className="flex-1 flex flex-col min-h-0">
            <CardHeader className="flex-shrink-0">
              <CardTitle>Campaign Leads</CardTitle>
              <CardDescription>
                Detailed status of each lead in this campaign
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1 overflow-auto p-0">
              <table className="w-full">
                <thead className="sticky top-0 bg-neutral-50 border-b border-neutral-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                      Lead
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                      SMS Sent
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                      Last Message
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200">
                  {campaign.campaign_leads?.map((cl: any) => (
                    <tr key={cl.id} className="hover:bg-neutral-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-neutral-900">
                        {cl.lead?.name || `Lead #${cl.lead_id}`}
                        <div className="text-xs text-neutral-500 font-normal">
                          {cl.lead?.phone}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            cl.status === "completed"
                              ? "bg-green-100 text-green-800"
                              : cl.status === "failed"
                              ? "bg-red-100 text-red-800"
                              : cl.status === "processing"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-neutral-100 text-neutral-800"
                          }`}
                        >
                          {cl.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-900">
                        {cl.sms_sent ? (
                          <CheckCircleIcon className="h-5 w-5 text-green-600" />
                        ) : (
                          <XCircleIcon className="h-5 w-5 text-neutral-300" />
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-neutral-500 max-w-xs truncate">
                        {cl.sms_message || "-"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => navigate(`/conversations/${cl.id}`)}
                        >
                          <ChatBubbleBottomCenterTextIcon className="h-4 w-4 mr-1" />
                          View Chat
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Live Feed (1/3 width) */}
        <div className="lg:col-span-1 h-full min-h-0">
          <LiveActivityFeed logs={logs || []} className="h-full" />
        </div>
      </div>
    </div>
  );
}
