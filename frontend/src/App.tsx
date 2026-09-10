import AppShell from "./components/AppShell";
import { useDashboard } from "./hooks/useDashboard";

export default function App() {
  const d = useDashboard();
  return (
    <div className="h-full w-full">
      <AppShell d={d} />
    </div>
  );
}
