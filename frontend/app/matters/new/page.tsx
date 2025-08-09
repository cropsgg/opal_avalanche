import { redirect } from 'next/navigation';
import { auth } from '@clerk/nextjs/server';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { MatterCreationForm } from '@/components/matters/MatterCreationForm';

export default async function NewMatterPage() {
  const { userId } = await auth();

  if (!userId) {
    redirect('/');
  }

  return (
    <div className="min-h-screen bg-cream-50">
      <DashboardHeader />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-display font-bold text-brown-900 mb-2">
            Create New Matter
          </h1>
          <p className="text-brown-500">
            Upload your documents and let OPAL analyze them for legal insights
          </p>
        </div>
        <MatterCreationForm />
      </div>
    </div>
  );
}
