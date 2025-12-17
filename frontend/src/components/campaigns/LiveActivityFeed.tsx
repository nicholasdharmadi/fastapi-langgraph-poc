import { useEffect, useRef } from "react";
import { formatDate } from "../../lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from "@heroicons/react/24/solid";

interface Log {
  id: number;
  created_at: string;
  level: string;
  node_name?: string;
  message: string;
}

interface LiveActivityFeedProps {
  logs: Log[];
  className?: string;
}

export function LiveActivityFeed({ logs, className }: LiveActivityFeedProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <Card className={`flex flex-col h-full ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <div className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </div>
          Live Activity Feed
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden p-0">
        <div
          ref={scrollRef}
          className="h-full overflow-y-auto p-4 space-y-4 bg-neutral-50/50"
        >
          {logs.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-neutral-400 text-sm">
              <ClockIcon className="h-8 w-8 mb-2 opacity-20" />
              <p>Waiting for activity...</p>
            </div>
          ) : (
            logs.map((log) => (
              <div
                key={log.id}
                className={`flex gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300`}
              >
                <div className="mt-1 flex-shrink-0">
                  {log.level === "ERROR" ? (
                    <XCircleIcon className="h-5 w-5 text-red-500" />
                  ) : log.node_name === "send_sms" ? (
                    <div className="h-5 w-5 rounded-full bg-blue-100 flex items-center justify-center">
                      <span className="text-[10px] font-bold text-blue-600">
                        S
                      </span>
                    </div>
                  ) : (
                    <CheckCircleIcon className="h-5 w-5 text-neutral-300" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-neutral-900 bg-white px-2 py-0.5 rounded border border-neutral-200">
                      {log.node_name || "System"}
                    </span>
                    <span className="text-[10px] text-neutral-400">
                      {formatDate(log.created_at)}
                    </span>
                  </div>
                  <div
                    className={`text-sm p-3 rounded-lg shadow-sm border ${
                      log.level === "ERROR"
                        ? "bg-red-50 border-red-100 text-red-900"
                        : "bg-white border-neutral-100 text-neutral-700"
                    }`}
                  >
                    {log.message}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
