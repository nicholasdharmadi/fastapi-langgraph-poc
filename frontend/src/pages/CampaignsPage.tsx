import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { campaignsApi, leadsApi } from "../services/api";
import { Link } from "react-router-dom";
import {
  PlusIcon,
  PlayIcon,
  EyeIcon,
  TrashIcon,
} from "@heroicons/react/24/solid";
import { getStatusColor, getStatusText, formatDate } from "../lib/utils";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";
import { PageLoader } from "../components/PageLoader";
import { CampaignWizard } from "../components/campaign-wizard/CampaignWizard";

export default function CampaignsPage() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const queryClient = useQueryClient();

  const { data: campaigns, isLoading } = useQuery({
    queryKey: ["campaigns"],
    queryFn: () => campaignsApi.list().then((res) => res.data),
    refetchInterval: 5000,
  });

  const { data: leads } = useQuery({
    queryKey: ["leads"],
    queryFn: () => leadsApi.list().then((res) => res.data),
  });

  const [deleteId, setDeleteId] = useState<number | null>(null);

  const deleteMutation = useMutation({
    mutationFn: (id: number) => campaignsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      setDeleteId(null);
    },
  });

  const startCampaignMutation = useMutation({
    mutationFn: (id: number) => campaignsApi.start(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
    },
  });

  if (isLoading) {
    return <PageLoader />;
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-neutral-900">
            Campaigns
          </h2>
          <p className="mt-2 text-neutral-600">Manage your SMS campaigns</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <PlusIcon className="h-4 w-4" />
          New Campaign
        </Button>
      </div>

      <div className="space-y-4">
        {campaigns && campaigns.length > 0 ? (
          campaigns.map((campaign) => (
            <Card
              key={campaign.id}
              className="hover:shadow-md transition-shadow"
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-xl">{campaign.name}</CardTitle>
                    {campaign.description && (
                      <CardDescription className="mt-2">
                        {campaign.description}
                      </CardDescription>
                    )}
                    <div className="mt-3 flex items-center gap-4 text-sm text-neutral-600">
                      <span>Type: {campaign.agent_type.toUpperCase()}</span>
                      <span>•</span>
                      <span>Created: {formatDate(campaign.created_at)}</span>
                      {campaign.stats && (
                        <>
                          <span>•</span>
                          <span>
                            Progress: {campaign.stats.completed}/
                            {campaign.stats.total_leads}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-3 py-1 text-xs font-medium text-white rounded-full ${getStatusColor(
                        campaign.status
                      )}`}
                    >
                      {getStatusText(campaign.status)}
                    </span>
                    {(campaign.status === "draft" ||
                      campaign.status === "pending") && (
                      <Button
                        size="sm"
                        onClick={() =>
                          startCampaignMutation.mutate(campaign.id)
                        }
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <PlayIcon className="h-3 w-3" />
                        Start
                      </Button>
                    )}
                    <Link to={`/campaigns/${campaign.id}`}>
                      <Button variant="outline" size="sm">
                        <EyeIcon className="h-3 w-3" />
                        View
                      </Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
                      onClick={() => setDeleteId(campaign.id)}
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>

                    <Dialog
                      open={deleteId === campaign.id}
                      onOpenChange={(open) => !open && setDeleteId(null)}
                    >
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Delete Campaign?</DialogTitle>
                          <DialogDescription>
                            This action cannot be undone. This will permanently
                            delete the campaign "{campaign.name}" and all
                            associated data.
                          </DialogDescription>
                        </DialogHeader>
                        <DialogFooter>
                          <Button
                            variant="outline"
                            onClick={() => setDeleteId(null)}
                          >
                            Cancel
                          </Button>
                          <Button
                            variant="destructive"
                            onClick={() => deleteMutation.mutate(campaign.id)}
                            disabled={deleteMutation.isPending}
                          >
                            {deleteMutation.isPending
                              ? "Deleting..."
                              : "Delete"}
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
              </CardHeader>
            </Card>
          ))
        ) : (
          <Card>
            <CardContent className="py-12 text-center text-neutral-500">
              No campaigns yet. Create your first campaign!
            </CardContent>
          </Card>
        )}
      </div>

      {showCreateModal && (
        <CampaignWizard
          onClose={() => setShowCreateModal(false)}
          totalLeads={leads?.length || 0}
        />
      )}
    </div>
  );
}
