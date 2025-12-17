import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { settingsApi } from '../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Spinner } from '../components/ui/spinner';
import { ClockIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/solid';

export function WorkingHoursCard() {
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);

  const { data: settings, isLoading } = useQuery({
    queryKey: ['working-hours'],
    queryFn: () => settingsApi.getWorkingHours().then((res) => res.data),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const [formData, setFormData] = useState({
    enforce_working_hours: settings?.enforce_working_hours ?? true,
    working_hours_start: settings?.working_hours_start ?? 9,
    working_hours_end: settings?.working_hours_end ?? 23,
    allow_weekend_sending: settings?.allow_weekend_sending ?? true,
  });

  // Update form when settings load
  useState(() => {
    if (settings) {
      setFormData({
        enforce_working_hours: settings.enforce_working_hours,
        working_hours_start: settings.working_hours_start,
        working_hours_end: settings.working_hours_end,
        allow_weekend_sending: settings.allow_weekend_sending,
      });
    }
  });

  const updateMutation = useMutation({
    mutationFn: (data: typeof formData) => settingsApi.updateWorkingHours(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['working-hours'] });
      setIsEditing(false);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate(formData);
  };

  const handleCancel = () => {
    if (settings) {
      setFormData({
        enforce_working_hours: settings.enforce_working_hours,
        working_hours_start: settings.working_hours_start,
        working_hours_end: settings.working_hours_end,
        allow_weekend_sending: settings.allow_weekend_sending,
      });
    }
    setIsEditing(false);
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-12 flex justify-center">
          <Spinner size="lg" />
        </CardContent>
      </Card>
    );
  }

  if (!settings) return null;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <ClockIcon className="h-5 w-5" />
              Working Hours
            </CardTitle>
            <CardDescription>Configure when campaigns can send messages</CardDescription>
          </div>
          {!isEditing && (
            <Button onClick={() => setIsEditing(true)} variant="outline" size="sm">
              Edit
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Current Status */}
          <div className="p-4 bg-neutral-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-neutral-700">Current Status</span>
              {settings.is_currently_allowed ? (
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircleIcon className="h-5 w-5" />
                  <span className="text-sm font-medium">Sending Allowed</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-red-600">
                  <XCircleIcon className="h-5 w-5" />
                  <span className="text-sm font-medium">Sending Blocked</span>
                </div>
              )}
            </div>
            <div className="text-sm text-neutral-600">
              Current time: {settings.current_hour}:00 on {settings.current_day}
            </div>
          </div>

          {isEditing ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Enforce Working Hours */}
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="enforce"
                  checked={formData.enforce_working_hours}
                  onChange={(e) =>
                    setFormData({ ...formData, enforce_working_hours: e.target.checked })
                  }
                  className="h-4 w-4 rounded border-neutral-300"
                />
                <Label htmlFor="enforce" className="cursor-pointer">
                  Enforce working hours restrictions
                </Label>
              </div>

              {/* Time Range */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start">Start Hour (24h format)</Label>
                  <Input
                    id="start"
                    type="number"
                    min="0"
                    max="23"
                    value={formData.working_hours_start}
                    onChange={(e) =>
                      setFormData({ ...formData, working_hours_start: parseInt(e.target.value) })
                    }
                    disabled={!formData.enforce_working_hours}
                  />
                  <p className="text-xs text-neutral-500">{formData.working_hours_start}:00</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="end">End Hour (24h format)</Label>
                  <Input
                    id="end"
                    type="number"
                    min="1"
                    max="24"
                    value={formData.working_hours_end}
                    onChange={(e) =>
                      setFormData({ ...formData, working_hours_end: parseInt(e.target.value) })
                    }
                    disabled={!formData.enforce_working_hours}
                  />
                  <p className="text-xs text-neutral-500">{formData.working_hours_end}:00</p>
                </div>
              </div>

              {/* Weekend Sending */}
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="weekend"
                  checked={formData.allow_weekend_sending}
                  onChange={(e) =>
                    setFormData({ ...formData, allow_weekend_sending: e.target.checked })
                  }
                  disabled={!formData.enforce_working_hours}
                  className="h-4 w-4 rounded border-neutral-300"
                />
                <Label
                  htmlFor="weekend"
                  className={formData.enforce_working_hours ? 'cursor-pointer' : 'opacity-50'}
                >
                  Allow weekend sending
                </Label>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                <Button type="submit" disabled={updateMutation.isPending}>
                  {updateMutation.isPending && <Spinner size="sm" className="mr-2" />}
                  Save Changes
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCancel}
                  disabled={updateMutation.isPending}
                >
                  Cancel
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-neutral-200">
                <span className="text-sm text-neutral-600">Enforcement</span>
                <span className="text-sm font-medium">
                  {settings.enforce_working_hours ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-neutral-200">
                <span className="text-sm text-neutral-600">Allowed Hours</span>
                <span className="text-sm font-medium">
                  {settings.working_hours_start}:00 - {settings.working_hours_end}:00
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-neutral-200">
                <span className="text-sm text-neutral-600">Weekend Sending</span>
                <span className="text-sm font-medium">
                  {settings.allow_weekend_sending ? 'Allowed' : 'Blocked'}
                </span>
              </div>
            </div>
          )}

          {/* Info Note */}
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-xs text-blue-900">
              <strong>Note:</strong> Changes are applied immediately but only persist for the
              current session. To make permanent changes, update the .env file and restart
              containers.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

