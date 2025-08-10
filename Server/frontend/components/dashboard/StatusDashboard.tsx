'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { healthApi, apiUtils } from '@/lib/api'
import { HealthStatus, Metrics } from '@/types'
import { 
  Loader2, 
  RefreshCw, 
  Activity, 
  Database, 
  Wifi, 
  WifiOff,
  AlertTriangle,
  CheckCircle,
  Server,
  HardDrive
} from 'lucide-react'
import { formatNumber, formatDate } from '@/lib/utils'

export default function StatusDashboard() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchData = async () => {
    setIsLoading(true)
    setError('')

    try {
      const [healthResponse, metricsResponse] = await Promise.all([
        healthApi.getDetailedHealth(),
        healthApi.getMetrics(),
      ])

      setHealth(healthResponse)
      setMetrics(metricsResponse)
      setLastUpdated(new Date())
    } catch (err) {
      setError(apiUtils.formatError(err))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'degraded':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />
      case 'unhealthy':
        return <AlertTriangle className="h-5 w-5 text-red-600" />
      default:
        return <Activity className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success'
      case 'degraded':
        return 'warning'
      case 'unhealthy':
        return 'destructive'
      default:
        return 'secondary'
    }
  }

  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getStatusIcon(health?.status || 'unknown')}
              <div>
                <CardTitle>System Status</CardTitle>
                <CardDescription>{health?.service || 'OPAL Server'} v{health?.version}</CardDescription>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {health && (
                <Badge variant={getStatusColor(health.status) as any}>
                  {health.status.toUpperCase()}
                </Badge>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={fetchData}
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="mr-2 h-4 w-4" />
                )}
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        
        {lastUpdated && (
          <CardContent>
            <p className="text-xs text-gray-500">
              Last updated: {formatDate(lastUpdated)}
            </p>
          </CardContent>
        )}
      </Card>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 text-red-800">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-medium">Error Loading Status</span>
            </div>
            <p className="mt-2 text-sm text-red-700">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Component Status */}
      {health?.components && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Qdrant Status */}
          {health.components.qdrant && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Database className="h-5 w-5" />
                  <span>Qdrant Vector Database</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Connection Status</span>
                  <Badge variant={health.components.qdrant.status === 'healthy' ? 'success' : 'destructive'}>
                    {health.components.qdrant.status}
                  </Badge>
                </div>

                {metrics?.qdrant && (
                  <>
                    {metrics.qdrant.vectors_count !== undefined && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Vectors</span>
                        <span className="font-mono text-sm">
                          {formatNumber(metrics.qdrant.vectors_count)}
                        </span>
                      </div>
                    )}

                    {metrics.qdrant.points_count !== undefined && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Points</span>
                        <span className="font-mono text-sm">
                          {formatNumber(metrics.qdrant.points_count)}
                        </span>
                      </div>
                    )}

                    {metrics.qdrant.name && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Collection</span>
                        <code className="text-xs bg-gray-100 px-1 rounded">
                          {metrics.qdrant.name}
                        </code>
                      </div>
                    )}
                  </>
                )}

                {health.components.qdrant.error && (
                  <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                    {health.components.qdrant.error}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Subnet Status */}
          {health.components.subnet && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  {health.components.subnet.connected ? (
                    <Wifi className="h-5 w-5 text-green-600" />
                  ) : (
                    <WifiOff className="h-5 w-5 text-red-600" />
                  )}
                  <span>Avalanche Subnet</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Connection</span>
                  <Badge variant={health.components.subnet.connected ? 'success' : 'destructive'}>
                    {health.components.subnet.connected ? 'Connected' : 'Disconnected'}
                  </Badge>
                </div>

                {health.components.subnet.chain_id && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Chain ID</span>
                    <span className="font-mono text-sm">
                      {health.components.subnet.chain_id}
                    </span>
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <span className="text-sm">Status</span>
                  <Badge variant={health.components.subnet.status === 'healthy' ? 'success' : 'destructive'}>
                    {health.components.subnet.status}
                  </Badge>
                </div>

                {health.components.subnet.error && (
                  <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                    {health.components.subnet.error}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Server className="h-5 w-5" />
            <span>Quick Actions</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button
              variant="outline"
              onClick={() => window.open('/api/v1/status', '_blank')}
              className="justify-start"
            >
              <Activity className="mr-2 h-4 w-4" />
              View Raw Status
            </Button>
            
            <Button
              variant="outline"
              onClick={() => window.open('/metrics', '_blank')}
              className="justify-start"
            >
              <HardDrive className="mr-2 h-4 w-4" />
              View Metrics
            </Button>
            
            <Button
              variant="outline"
              onClick={() => window.open('/health/detailed', '_blank')}
              className="justify-start"
            >
              <CheckCircle className="mr-2 h-4 w-4" />
              Detailed Health
            </Button>
          </div>
        </CardContent>
      </Card>

      {!health && !error && !isLoading && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8 text-gray-500">
              <Activity className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Unable to load system status</p>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchData}
                className="mt-4"
              >
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
