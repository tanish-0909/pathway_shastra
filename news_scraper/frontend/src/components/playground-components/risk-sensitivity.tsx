import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

// Type definition s
export interface RiskSensitivityData {
  instrument: string
  dv01: string
  pvbp: number
  vega: number | "N/A"
  gamma: number
  theta: number
}

export interface RiskSensitivityTableProps {
  title?: string
  subtitle?: string
  data: RiskSensitivityData[]
}

export function RiskSensitivityTable({
  title = "Risk Sensitivity",
  subtitle = "Rates / FX Greeks",
  data,
}: RiskSensitivityTableProps) {
  const formatValue = (value: number | "N/A", decimals = 3): string => {
    if (value === "N/A") return "N/A"
    return value.toFixed(decimals)
  }

  return (
    <Card className="w-full bg-[#0f2a2a] border-[#1e3a3a]">
      <CardHeader>
        <CardTitle className="text-white text-xl font-semibold">{title}</CardTitle>
        <CardDescription className="text-slate-400 text-sm">{subtitle}</CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="border-[#1e3a3a] hover:bg-[#1e3a3a]/30">
              <TableHead className="text-slate-400 font-medium text-xs uppercase tracking-wider">INSTRUMENT</TableHead>
              <TableHead className="text-slate-400 font-medium text-xs uppercase tracking-wider text-right">
                DV01
              </TableHead>
              <TableHead className="text-slate-400 font-medium text-xs uppercase tracking-wider text-right">
                PVBP
              </TableHead>
              <TableHead className="text-slate-400 font-medium text-xs uppercase tracking-wider text-right">
                VEGA
              </TableHead>
              <TableHead className="text-slate-400 font-medium text-xs uppercase tracking-wider text-right">
                GAMMA
              </TableHead>
              <TableHead className="text-slate-400 font-medium text-xs uppercase tracking-wider text-right">
                THETA
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row, index) => (
              <TableRow key={index} className="border-[#1e3a3a] hover:bg-[#1e3a3a]/30">
                <TableCell className="font-medium text-white py-5">{row.instrument}</TableCell>
                <TableCell className="text-slate-200 text-right py-5">{row.dv01}</TableCell>
                <TableCell className="text-slate-200 text-right py-5">{formatValue(row.pvbp)}</TableCell>
                <TableCell className="text-slate-200 text-right py-5">
                  {row.vega === "N/A" ? "N/A" : formatValue(row.vega, 1)}
                </TableCell>
                <TableCell className="text-slate-200 text-right py-5">{formatValue(row.gamma, 2)}</TableCell>
                <TableCell className="text-slate-200 text-right py-5">{formatValue(row.theta, 1)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
