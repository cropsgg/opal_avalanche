import { redirect } from 'next/navigation';
import { auth } from '@clerk/nextjs/server';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { MattersGrid } from '@/components/dashboard/MattersGrid';
import { DashboardStats } from '@/components/dashboard/DashboardStats';

export default async function DashboardPage() {
  const { userId } = await auth();

  if (!userId) {
    redirect('/');
  }

  return (
    <div className="min-h-screen bg-cream-50">
      <DashboardHeader />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <DashboardStats />
        <MattersGrid />
      </div>
    </div>
  );
}
