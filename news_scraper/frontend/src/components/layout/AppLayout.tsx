import { useState, useCallback, useRef, useEffect } from 'react'
import { Sidebar, type SidebarItem } from './Sidebar'
import { useAsset } from '@/context/AssetContext'
import type { Asset } from '@/components/explore-assets/data/types'

import { Layout, Model, TabNode, Actions, DockLocation, type IJsonModel, type ITabRenderValues } from 'flexlayout-react'
// dark.css is now imported in main.tsx before index.css to allow overrides
import { TopBar, type Tab } from './TopBar' // Keeping types, but TopBar might be redundant if we use FlexLayout's tabs

interface AppLayoutProps {
  sidebarItems: SidebarItem[]
  defaultTab: Tab
  initialTabs?: Tab[]
}

export function AppLayout({ sidebarItems, defaultTab, initialTabs }: AppLayoutProps) {
  const [activeTabId, setActiveTabId] = useState<string>(initialTabs?.[0]?.id || defaultTab.id)
  const { setSelectedAsset, setNavigateToAsset, setAssetForTab, getAssetForTab, setCurrentTabId } = useAsset()
  
  // Create a map of components for easy lookup
  const componentMap = useRef<Record<string, React.ComponentType>>({}).current
  sidebarItems.forEach(item => {
    componentMap[item.id] = item.component
  })

  // Initial Model
  const json: IJsonModel = {
    global: {
      tabEnableClose: true,
      tabEnableRename: false,
      tabSetEnableMaximize: true,
      tabClassName: "custom-tab",
      splitterSize: 6,
      splitterExtra: 0,
      enableEdgeDock: true,
    },
    borders: [],
    layout: {
      type: "row",
      weight: 100,
      children: [
        {
          type: "tabset",
          weight: 50,
          id: "main-tabset",
          children: (initialTabs || [defaultTab]).map(tab => ({
            type: "tab",
            name: tab.label,
            component: tab.id,
            id: tab.id,
            enableClose: tab.closeable !== false
          }))
        }
      ]
    }
  }

  const [model] = useState(() => Model.fromJson(json))

  // Handle navigation to asset detail pages
  const handleAssetNavigation = useCallback((asset: Asset) => {
    // Map asset type to the corresponding view
    const assetTypeToView: Record<string, { id: string; label: string }> = {
      bonds: { id: 'bonds', label: 'Bonds' },
      stocks: { id: 'stocks', label: 'Stocks' },
      etfs: { id: 'etfs', label: 'ETFs' },
      commodities: { id: 'commodities', label: 'Commodities' },
    }

    const viewConfig = assetTypeToView[asset.assetType]
    if (!viewConfig) return

    // Create a unique tab ID for this specific asset
    const tabId = `${viewConfig.id}-${asset.id}`
    const tabName = `${asset.name}`

    // Store the asset for this specific tab
    setAssetForTab(tabId, asset)
    
    // Set as current selected asset and tab
    setSelectedAsset(asset)
    setCurrentTabId(tabId)

    // Check if tab already exists
    const existingNode = model.getNodeById(tabId)

    if (existingNode) {
      model.doAction(Actions.selectTab(tabId))
    } else {
      // Find the currently active tabset to add the new tab there
      const activeTabset = model.getActiveTabset()
      const targetTabsetId = activeTabset ? activeTabset.getId() : 'main-tabset'

      // Add new tab with the asset type as component (bonds, stocks, etc.)
      model.doAction(
        Actions.addNode(
          {
            type: 'tab',
            component: viewConfig.id,
            name: tabName,
            id: tabId,
            enableClose: true,
          },
          targetTabsetId,
          DockLocation.CENTER,
          -1
        )
      )
    }

    setActiveTabId(tabId)
  }, [model, setSelectedAsset, setAssetForTab, setCurrentTabId])

  // Register the navigation function with context
  useEffect(() => {
    setNavigateToAsset(handleAssetNavigation)
    return () => setNavigateToAsset(null)
  }, [handleAssetNavigation, setNavigateToAsset])

  const factory = (node: TabNode) => {                                                              
    const componentId = node.getComponent()
    const Component = componentMap[componentId as string]
    if (Component) {
      return <Component />
    }
    return <div>Component not found</div>
  }

  // Simple tab render - just use the name, styling handled by CSS
  const onRenderTab = (node: TabNode, renderValues: ITabRenderValues) => {
    renderValues.content = node.getName();
  };

  const handleSidebarItemClick = useCallback((itemId: string) => {
    const sidebarItem = sidebarItems.find(item => item.id === itemId)
    if (!sidebarItem) return

    setActiveTabId(itemId)

    // Check if tab already exists
    const existingNode = model.getNodeById(itemId)
    
    if (existingNode) {
      model.doAction(Actions.selectTab(itemId))
    } else {
      // Find the currently active tabset to add the new tab there
      const activeTabset = model.getActiveTabset();
      const targetTabsetId = activeTabset ? activeTabset.getId() : "main-tabset";
      
      // Add new tab to the active tabset
      model.doAction(Actions.addNode({
        type: "tab",
        component: itemId,
        name: sidebarItem.label,
        id: itemId,
        enableClose: true
      }, targetTabsetId, DockLocation.CENTER, -1))
    }
  }, [sidebarItems, model])

  // Sync active tab state when user clicks tabs in layout or closes tabs
  const onAction = (action: any) => {
    if (action.type === "FlexLayout_SelectTab") {
      const tabId = action.data.tabNode
      setActiveTabId(tabId)
      setCurrentTabId(tabId)
      
      // Update selected asset when switching to an asset tab
      const assetForTab = getAssetForTab(tabId)
      if (assetForTab) {
        setSelectedAsset(assetForTab)
      }
    }
    
    // When a tab is deleted, update activeTabId to the newly selected tab
    if (action.type === "FlexLayout_DeleteTab") {
      // After delete, find the active tab in the model
      setTimeout(() => {
        const activeTabset = model.getActiveTabset()
        if (activeTabset) {
          const selectedNode = activeTabset.getSelectedNode()
          if (selectedNode) {
            const tabId = selectedNode.getId()
            setActiveTabId(tabId)
            setCurrentTabId(tabId)
            
            // Update selected asset for the new active tab
            const assetForTab = getAssetForTab(tabId)
            if (assetForTab) {
              setSelectedAsset(assetForTab)
            }
          }
        }
      }, 0)
    }
    return action
  }

  return (
    <div className="flex min-h-screen w-screen bg-background">
      <Sidebar 
        items={sidebarItems}
        activeItem={activeTabId}
        onItemClick={handleSidebarItemClick}
      />
      <div className="flex-1 flex flex-col bg-background overflow-hidden">
        {/* Main Content with Split View - TopBar integrated */}
        <div className="flex-1 relative">
          <div className="absolute top-[5px] right-3 z-50 flex items-center">
            <TopBar tabs={[]} />
          </div>
          <Layout
            model={model}
            factory={factory}
            onAction={onAction}
            onRenderTab={onRenderTab}
          />
        </div>
      </div>
    </div>
  )
}
