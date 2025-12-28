interface Asset {
  label: string
  name: string
  yield: number
  duration: number
  convexity: number
}

interface ComparisonViewData {
  assetA: Asset
  assetB: Asset
}

interface ComparisonViewProps {
  data: ComparisonViewData
  title?: string
  subtitle?: string
}

function AssetCard({ asset }: { asset: Asset }) {
  return (
    <div className="flex-1">
      <p className="text-gray-400 text-sm mb-4">{asset.label}</p>

      <p className="text-white text-lg mb-1">{asset.name}</p>
      <p className="text-white text-4xl font-bold mb-6">Yield: {asset.yield.toFixed(2)}%</p>

      <div className="border-t border-[#2dd4bf] pt-4 mb-4">
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Duration:</span>
          <span className="text-white text-lg">{asset.duration}</span>
        </div>
      </div>

      <div className="border-t border-[#2dd4bf] pt-4">
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Conv:</span>
          <span className="text-white text-lg">{asset.convexity}</span>
        </div>
      </div>
    </div>
  )
}

export function ComparisonView({
  data,
  title = "Comparison View",
  subtitle = "Instrument Comparison",
}: ComparisonViewProps) {
  return (
    <div className="bg-[#0d2a2d] rounded-2xl p-8 border border-[#1a4a4a]">
      <h2 className="text-white text-2xl font-bold mb-1">{title}</h2>
      <p className="text-gray-400 mb-6">{subtitle}</p>

      <div className="border-t border-[#2dd4bf] mb-8" />

      <div className="flex gap-8">
        <AssetCard asset={data.assetA} />
        <AssetCard asset={data.assetB} />
      </div>
    </div>
  )
}
