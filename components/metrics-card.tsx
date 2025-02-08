import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface MetricsCardProps {
  title: string
  value: string | number
  change?: {
    value: number
    label: string
  }
}

export function MetricsCard({ title, value, change }: MetricsCardProps) {
  return (
    <Card className="bg-white/50 backdrop-blur-sm border-neutral-200/50">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-neutral-600">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2">
          <div className="text-2xl font-bold">{value}</div>
          {change && (
            <div className="text-xs text-neutral-500">
              {change.value >= 0 ? "+" : ""}
              {change.value} {change.label}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

