import { IDEShell } from "@/components/ide/IDEShell";
import { ProtectedRoute } from "@/components/protected-route";

interface IDEPageProps {
  params: Promise<{ projectId: string }>;
}

export default async function IDEPage({ params }: IDEPageProps) {
  const { projectId } = await params;

  return (
    <ProtectedRoute>
      <IDEShell projectId={projectId} projectName="Agent Phantom" />
    </ProtectedRoute>
  );
}

export const metadata = {
  title: "Antigravity IDE — Agent Phantom",
  description: "Autonomous engineering workspace",
};
