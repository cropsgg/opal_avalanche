import StatusDashboard from '@/components/dashboard/StatusDashboard'
import { Activity } from 'lucide-react'

export default function StatusPage() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center space-x-2">
          <Activity className="h-8 w-8" />
          <span>System Status</span>
        </h1>
        <p className="text-gray-600">
          Monitor blockchain connectivity, database health, and system performance
        </p>
      </div>

      {/* Status Dashboard */}
      <StatusDashboard />
    </div>
  )
}
