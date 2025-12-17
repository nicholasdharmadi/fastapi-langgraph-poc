import * as React from "react";
import { cn } from "../../lib/utils";

const Checkbox = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => (
  <input
    type="checkbox"
    className={cn(
      "peer h-4 w-4 shrink-0 rounded-sm border border-neutral-900 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neutral-950 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 accent-black",
      className
    )}
    ref={ref}
    {...props}
  />
));
Checkbox.displayName = "Checkbox";

export { Checkbox };
