"use client";

import { useState, useMemo } from "react";
import { Search, SlidersHorizontal } from "lucide-react";
import { MarketIndexCard } from "../components/explore-assets/market-index-card";
import { FilterDropdown } from "../components/explore-assets/filter-dropdown";
import { AssetTable } from "../components/explore-assets/asset-table";
// import { Sidebar } from "./sidebar"
// import { Header } from "./header"
import {
  marketIndices,
  assets,
  assetClassOptions,
  regionOptions,
  sectorOptions,
} from "../components/explore-assets/data/assets-data";
import type {
  Asset,
  MarketIndex,
} from "../components/explore-assets/data/types";

export function ExploreAssets() {
  const [searchQuery, setSearchQuery] = useState("");
  const [showHeldOnly, setShowHeldOnly] = useState(false);
  const [assetClass, setAssetClass] = useState("all");
  const [region, setRegion] = useState("all");
  const [sector, setSector] = useState("all");
  const [activeNav, setActiveNav] = useState("assets");
  const [selectedIndex, setSelectedIndex] = useState<MarketIndex | null>(null);

  const filteredAssets = useMemo(() => {
    return assets.filter((asset) => {
      const matchesSearch =
        asset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        asset.ticker.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesHeld = !showHeldOnly || asset.isHeld;
      const matchesAssetClass =
        assetClass === "all" || asset.assetType === assetClass;
      const matchesRegion = region === "all" || asset.region === region;
      const matchesSector = sector === "all" || asset.sector === sector;

      return (
        matchesSearch &&
        matchesHeld &&
        matchesAssetClass &&
        matchesRegion &&
        matchesSector
      );
    });
  }, [searchQuery, showHeldOnly, assetClass, region, sector]);

  const handleIndexClick = (index: MarketIndex) => {
    setSelectedIndex(selectedIndex?.id === index.id ? null : index);
  };

  const handleTrade = (asset: Asset) => {
    alert(`Opening trade dialog for ${asset.name} (${asset.ticker})`);
  };

  const clearFilters = () => {
    setSearchQuery("");
    setShowHeldOnly(false);
    setAssetClass("all");
    setRegion("all");
    setSector("all");
  };

  const hasActiveFilters =
    searchQuery ||
    showHeldOnly ||
    assetClass !== "all" ||
    region !== "all" ||
    sector !== "all";

  const getAssetTypeLabel = () => {
    const option = assetClassOptions.find((opt) => opt.value === assetClass);
    return option?.label || "Assets";
  };

  return (
    <div className="min-h-screen bg-background text-primary flex">
      {/* <Sidebar activeItem={activeNav} onItemClick={setActiveNav} /> */}

      <div className="flex-1 flex flex-col">
        {/* <Header /> */}

        <main className="flex-1 p-8 overflow-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2 text-primary">
              Explore Assets
            </h1>
            <p className="text-[#6b7a8f]">
              Discover investment opportunities tailored for your firm.
            </p>
          </div>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto mb-6">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#6b7a8f]" />
            <input
              type="text"
              placeholder="Search by asset name, ticker, ISIN..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#0f1a24] border border-[#1e3a5f] rounded-full py-3 pl-12 pr-4 text-[#e2e8f0] placeholder-[#6b7a8f] focus:outline-none focus:ring-2 focus:ring-[#14b8a6]/50 focus:border-[#14b8a6]/50 transition-all"
            />
          </div>

          {/* Filters */}
          <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
            <label className="flex items-center gap-3 cursor-pointer group">
              <button
                role="switch"
                aria-checked={showHeldOnly}
                onClick={() => setShowHeldOnly(!showHeldOnly)}
                className={`
                  relative w-12 h-6 rounded-full transition-colors duration-200
                  ${showHeldOnly ? "bg-[#14b8a6]" : "bg-[#1e3a5f]"}
                `}
              >
                <div
                  className={`
                    absolute top-1 w-4 h-4 bg-[#e2e8f0] rounded-full transition-transform duration-200
                    ${showHeldOnly ? "translate-x-7" : "translate-x-1"}
                  `}
                />
              </button>
              <span className="text-[#6b7a8f] text-sm group-hover:text-[#e2e8f0] transition-colors">
                Show My Held Assets Only
              </span>
            </label>

            <div className="flex gap-3 flex-wrap">
              <FilterDropdown
                label="Asset Class"
                options={assetClassOptions}
                value={assetClass}
                onChange={setAssetClass}
              />
              <FilterDropdown
                label="Region"
                options={regionOptions}
                value={region}
                onChange={setRegion}
              />
              <FilterDropdown
                label="Sector"
                options={sectorOptions}
                value={sector}
                onChange={setSector}
              />
              <button
                className={`
                  flex items-center gap-2 bg-[#0f1a24] border border-[#1e3a5f] 
                  text-[#6b7a8f] text-sm rounded-lg px-4 py-2 
                  hover:bg-[#132636] hover:border-[#14b8a6]/30 transition-all duration-200
                `}
              >
                More Filters
                <SlidersHorizontal className="w-4 h-4" />
              </button>

              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="text-sm text-[#14b8a6] hover:text-[#14b8a6]/80 hover:underline transition-colors"
                >
                  Clear all
                </button>
              )}
            </div>
          </div>

          {/* Key Market Indices */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold mb-4 text-[#e2e8f0]">
              Key Market Indices
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {marketIndices.map((index) => (
                <MarketIndexCard
                  key={index.id}
                  index={index}
                  onClick={handleIndexClick}
                />
              ))}
            </div>
            {selectedIndex && (
              <div className="mt-4 p-4 bg-[#0f1a24] border border-[#14b8a6]/30 rounded-lg animate-in fade-in slide-in-from-top-2 duration-200">
                <p className="text-[#e2e8f0]">
                  Selected:{" "}
                  <span className="font-bold">{selectedIndex.name}</span> -
                  Current value:{" "}
                  <span className="font-mono">
                    {selectedIndex.value.toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                    })}
                  </span>
                </p>
              </div>
            )}
          </div>

          <div className="bg-[#0a1018] rounded-lg border border-[#1e3a5f] overflow-hidden">
            <AssetTable
              assets={filteredAssets}
              assetType={assetClass}
              onTrade={handleTrade}
            />
            {filteredAssets.length === 0 && (
              <div className="p-8 text-center text-[#6b7a8f]">
                <p>
                  No {assetClass === "all" ? "assets" : assetClass} match your
                  current filters.
                </p>
                <button
                  onClick={clearFilters}
                  className="mt-2 text-[#14b8a6] hover:underline"
                >
                  Clear filters
                </button>
              </div>
            )}
          </div>

          {/* Results count */}
          <div className="mt-4 text-sm text-[#6b7a8f]">
            Showing {filteredAssets.length} of {assets.length} assets
            {assetClass !== "all" && (
              <span className="text-[#14b8a6]">
                {" "}
                (filtered by {getAssetTypeLabel()})
              </span>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
