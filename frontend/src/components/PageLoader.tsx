import { Spinner } from "./ui/spinner";

export function PageLoader() {
  return (
    <div className="flex items-center justify-center h-[calc(100vh-200px)]">
      <div className="flex flex-col items-center gap-4">
        <Spinner size="lg" className="text-blue-600" />
        <p className="text-neutral-500 animate-pulse">Loading...</p>
      </div>
    </div>
  );
}
