import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "../services/api";
import {
  ChartBarIcon,
  UserGroupIcon,
  CheckCircleIcon,
  ChatBubbleLeftRightIcon,
} from "@heroicons/react/24/solid";
import { getStatusColor, getStatusText, formatDate } from "../lib/utils";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { PageLoader } from "../components/PageLoader";
import { WorkingHoursCard } from "../components/WorkingHoursCard";

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: () => dashboardApi.getStats().then((res) => res.data),
    refetchInterval: 5000,
  });

  const { data: recentCampaigns, isLoading: campaignsLoading } = useQuery({
    queryKey: ["recent-campaigns"],
    queryFn: () => dashboardApi.getRecentCampaigns(5).then((res) => res.data),
    refetchInterval: 5000,
  });

  if (statsLoading || campaignsLoading) {
    return <PageLoader />;
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-neutral-900">
          Dashboard
        </h2>
        <p className="mt-2 text-neutral-600">
          Overview of your SMS campaigns and leads
        </p>
      </div>

      {/* Working Hours Configuration */}
      <WorkingHoursCard />

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Campaigns
            </CardTitle>
            <ChartBarIcon className="h-4 w-4 text-neutral-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.campaigns.total || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Leads</CardTitle>
            <UserGroupIcon className="h-4 w-4 text-neutral-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.leads.total || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">SMS Sent</CardTitle>
            <ChatBubbleLeftRightIcon className="h-4 w-4 text-neutral-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.leads.sms_sent || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircleIcon className="h-4 w-4 text-neutral-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.leads.success_rate.toFixed(1) || 0}%
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Campaigns */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Campaigns</CardTitle>
          <CardDescription>Your most recent campaign activity</CardDescription>
        </CardHeader>
        <CardContent>
          {recentCampaigns && recentCampaigns.length > 0 ? (
            <div className="space-y-3">
              {recentCampaigns.map((campaign) => (
                <div
                  key={campaign.id}
                  className="flex items-center justify-between p-4 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors"
                >
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-neutral-900">
                      {campaign.name}
                    </h4>
                    <p className="text-sm text-neutral-500">
                      Created {formatDate(campaign.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span
                      className={`px-3 py-1 text-xs font-medium text-white rounded-full ${getStatusColor(
                        campaign.status
                      )}`}
                    >
                      {getStatusText(campaign.status)}
                    </span>
                    {campaign.stats && (
                      <div className="text-sm text-neutral-500">
                        {campaign.stats.completed}/{campaign.stats.total_leads}{" "}
                        completed
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-neutral-500">No campaigns yet</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
