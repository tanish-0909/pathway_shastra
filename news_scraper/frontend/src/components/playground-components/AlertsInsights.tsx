"use client"

import { AlertTriangle, Info } from "lucide-react"
export interface Alert {
  id: string
  title: string
  timestamp: string
  severity: "critical" | "warning" | "info"
  icon: "alert-triangle" | "exclamation" | "info"
}

interface AlertsInsightsProps {
  alerts?: Alert[]
  // Support for direct array data from schema
  [key: number]: Alert
}

export function AlertsInsights(props: AlertsInsightsProps | Alert[]) {
  // Handle both array and object with alerts property 
  const alerts: Alert[] = Array.isArray(props) 
    ? props 
    : (props as AlertsInsightsProps).alerts || Object.values(props).filter((v): v is Alert => 
        typeof v === 'object' && v !== null && 'id' in v && 'title' in v
      );
  const getIconBgColor = (severity: Alert["severity"]) => {
    switch (severity) {
      case "critical":
        return "bg-[#3d1f1f]"
      case "warning":
        return "bg-[#3d3a1f]"
      case "info":
        return "bg-[#1f3d3d]"
      default:
        return "bg-gray-800"
    }
  }

  const getIconColor = (severity: Alert["severity"]) => {
    switch (severity) {
      case "critical":
        return "text-[#d63031]"
      case "warning":
        return "text-[#fdcb6e]"
      case "info":
        return "text-[#00b894]"
      default:
        return "text-gray-400"
    }
  }

  const getBadgeColor = (severity: Alert["severity"]) => {
    switch (severity) {
      case "critical":
        return "border-[#d63031] text-[#d63031]"
      case "warning":
        return "border-[#fdcb6e] text-[#fdcb6e]"
      case "info":
        return "border-[#00b894] text-[#00b894]"
      default:
        return "border-gray-400 text-gray-400"
    }
  }

  const getBadgeLabel = (severity: Alert["severity"]) => {
    switch (severity) {
      case "critical":
        return "Critical"
      case "warning":
        return "Warning"
      case "info":
        return "Info"
      default:
        return severity
    }
  }

  const renderIcon = (iconType: Alert["icon"], severity: Alert["severity"]) => {
    const iconClass = `w-6 h-6 ${getIconColor(severity)}`

    switch (iconType) {
      case "alert-triangle":
        return <AlertTriangle className={iconClass} />
      case "exclamation":
        return <span className={`text-2xl font-bold ${getIconColor(severity)}`}>!</span>
      case "info":
        return <Info className={iconClass} />
      default:
        return null
    }
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-8">
      <div className="bg-background rounded-3xl p-10 shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <h1 className="text-4xl font-bold text-[#ffffff]">Alerts & Insights</h1>
          <div className="flex items-center gap-8">
            <button className="text-[#a8a8a8] hover:text-[#ffffff] transition-colors text-lg font-medium">
              Mute
            </button>
            <button className="text-[#a8a8a8] hover:text-[#ffffff] transition-colors text-lg font-medium">
              Clear
            </button>
          </div>
        </div>

        {/* Alerts List */}
        <div className="space-y-6">
          {alerts.map((alert) => (
            <div key={alert.id} className="flex items-center gap-6 py-4">
              {/* Icon */}
              <div
                className={`flex items-center justify-center w-16 h-16 rounded-full flex-shrink-0 ${getIconBgColor(
                  alert.severity,
                )}`}
              >
                {renderIcon(alert.icon, alert.severity)}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <h3 className="text-[#ffffff] text-xl font-normal mb-1">{alert.title}</h3>
                <p className="text-[#a8a8a8] text-base">{alert.timestamp}</p>
              </div>

              {/* Badge */}
              <div
                className={`px-6 py-2 rounded-full border-2 ${getBadgeColor(
                  alert.severity,
                )} font-medium text-base flex-shrink-0`}
              >
                {getBadgeLabel(alert.severity)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
