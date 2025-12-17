import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import DashboardPage from "./pages/DashboardPage";
import CampaignsPage from "./pages/CampaignsPage";
import CampaignDetailPage from "./pages/CampaignDetailPage";
import LeadsPage from "./pages/LeadsPage";
import WorkflowsPage from "./pages/WorkflowsPage";
import WorkflowEditorPage from "./pages/WorkflowEditorPage";
import AgentsPage from "./pages/AgentsPage";
import ConversationDetailPage from "./pages/ConversationDetailPage";
import PromptBuilderPage from "./pages/PromptBuilderPage";
import {
  ChartBarIcon,
  UserGroupIcon,
  MegaphoneIcon,
  RectangleStackIcon,
  CpuChipIcon,
  MicrophoneIcon,
} from "@heroicons/react/24/solid";
import { cn } from "./lib/utils";

const queryClient = new QueryClient();

function Navigation() {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === "/") {
      return location.pathname === "/";
    }
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="border-b border-neutral-200 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="hidden sm:flex sm:gap-1">
              <Link
                to="/"
                className={cn(
                  "inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors",
                  isActive("/") && location.pathname === "/"
                    ? "bg-neutral-900 text-white"
                    : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900"
                )}
              >
                <ChartBarIcon className="h-4 w-4" />
                Dashboard
              </Link>
              <Link
                to="/campaigns"
                className={cn(
                  "inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors",
                  isActive("/campaigns")
                    ? "bg-neutral-900 text-white"
                    : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900"
                )}
              >
                <MegaphoneIcon className="h-4 w-4" />
                Campaigns
              </Link>
              <Link
                to="/leads"
                className={cn(
                  "inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors",
                  isActive("/leads")
                    ? "bg-neutral-900 text-white"
                    : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900"
                )}
              >
                <UserGroupIcon className="h-4 w-4" />
                Leads
              </Link>
              <Link
                to="/workflows"
                className={cn(
                  "inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors",
                  isActive("/workflows")
                    ? "bg-neutral-900 text-white"
                    : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900"
                )}
              >
                <RectangleStackIcon className="h-4 w-4" />
                Workflows
              </Link>
              <Link
                to="/agents"
                className={cn(
                  "inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors",
                  isActive("/agents")
                    ? "bg-neutral-900 text-white"
                    : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900"
                )}
              >
                <CpuChipIcon className="h-4 w-4" />
                Agents
              </Link>
              <Link
                to="/prompt-builder"
                className={cn(
                  "inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors",
                  isActive("/prompt-builder")
                    ? "bg-neutral-900 text-white"
                    : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900"
                )}
              >
                <MicrophoneIcon className="h-4 w-4" />
                Prompt Builder
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-neutral-50">
          <Navigation />
          <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/campaigns" element={<CampaignsPage />} />
              <Route path="/campaigns/:id" element={<CampaignDetailPage />} />
              <Route
                path="/conversations/:campaignLeadId"
                element={<ConversationDetailPage />}
              />
              <Route path="/leads" element={<LeadsPage />} />
              <Route path="/workflows" element={<WorkflowsPage />} />
              <Route path="/workflows/:id" element={<WorkflowEditorPage />} />
              <Route path="/agents" element={<AgentsPage />} />
              <Route path="/prompt-builder" element={<PromptBuilderPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
