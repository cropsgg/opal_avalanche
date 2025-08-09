import { redirect } from 'next/navigation';
import { auth } from '@clerk/nextjs/server';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { MatterWorkspace } from '@/components/matters/MatterWorkspace';

interface MatterPageProps {
  params: {
    id: string;
  };
  searchParams: {
    created?: string;
  };
}

export default async function MatterPage({ params, searchParams }: MatterPageProps) {
  const { userId } = await auth();

  if (!userId) {
    redirect('/');
  }

  const isNewlyCreated = searchParams.created === 'true';

  return (
    <div className="min-h-screen bg-cream-50">
      <DashboardHeader />
      <MatterWorkspace matterId={params.id} isNewlyCreated={isNewlyCreated} />
    </div>
  );
}
