import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { workflowsApi } from "../services/api";
import { Link } from "react-router-dom";
import { PlusIcon, PencilIcon, TrashIcon } from "@heroicons/react/24/solid";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { PageLoader } from "../components/PageLoader";
import { formatDate } from "../lib/utils";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";

export default function WorkflowsPage() {
  const queryClient = useQueryClient();
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const { data: workflows, isLoading } = useQuery({
    queryKey: ["workflows"],
    queryFn: () => workflowsApi.list().then((res) => res.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => workflowsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
      setDeleteId(null);
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
            Workflows
          </h2>
          <p className="mt-2 text-neutral-600">
            Manage your campaign automation workflows
          </p>
        </div>
        <Link to="/workflows/new">
          <Button>
            <PlusIcon className="h-4 w-4 mr-2" />
            New Workflow
          </Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {workflows && workflows.length > 0 ? (
          workflows.map((workflow) => (
            <Card
              key={workflow.id}
              className="hover:shadow-md transition-shadow"
            >
              <CardHeader>
                <CardTitle className="flex justify-between items-start">
                  <span className="truncate">{workflow.name}</span>
                  <div className="flex gap-2">
                    <Link to={`/workflows/${workflow.id}`}>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <PencilIcon className="h-4 w-4 text-neutral-500" />
                      </Button>
                    </Link>
                    <Dialog
                      open={deleteId === workflow.id}
                      onOpenChange={(open) => !open && setDeleteId(null)}
                    >
                      <DialogTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                          onClick={() => setDeleteId(workflow.id)}
                        >
                          <TrashIcon className="h-4 w-4 text-red-500" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Delete Workflow?</DialogTitle>
                          <DialogDescription>
                            This action cannot be undone. This will permanently
                            delete the workflow "{workflow.name}".
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
                            onClick={() => deleteMutation.mutate(workflow.id)}
                          >
                            Delete
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>
                </CardTitle>
                <CardDescription>
                  {workflow.description || "No description"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-xs text-neutral-500">
                  Created: {formatDate(workflow.created_at)}
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="col-span-full">
            <Card>
              <CardContent className="py-12 text-center text-neutral-500">
                No workflows yet. Create your first workflow to automate your
                campaigns!
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
