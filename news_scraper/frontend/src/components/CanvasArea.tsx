// src/components/CanvasArea.tsx
import React from "react";
import { usePlayground } from "../context/PlaygroundContext";
import { ComponentMap } from "./playground-components";

type AnyObject = { [k: string]: any };

export interface CanvasComponentConfig {
  id?: string;
  type: string;
  data?: AnyObject;
}

/**
 * CanvasArea - renders the currently selected version's components.
 * This grid forces components to stretch to card area; components should
 * be implemented to use full width (w-full) and responsive sizing.
 */
export const CanvasArea: React.FC = () => {
  const { currentVersion, isLoading } = usePlayground();

  if (!currentVersion) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#0f1419] p-8">
        <div className="text-center">
          <h1 className="text-5xl font-bold mb-3 text-white">Ready to begin?</h1>
          <p className="text-gray-400 text-lg">Explore with Playground</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#0f1419]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto mb-4"></div>
          <p className="text-gray-400">Generating canvas...</p>
        </div>
      </div>
    );
  }

  const componentsArray: CanvasComponentConfig[] = Array.isArray(
    currentVersion.components,
  )
    ? (currentVersion.components as CanvasComponentConfig[])
    : [];

  return (
    <main className="flex-1 overflow-auto bg-[#0a0e14] p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">
              Version {currentVersion.versionNumber}
            </h2>
          </div>
        </div>

        {/* Responsive grid:
            - 1 col on mobile, 2 on md, 3 on lg
            - each grid cell is a flex column that stretches
            - auto-rows-min keeps cells flexible; use min-h to avoid tiny cards
        */}
        <div
          className="
            grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6
            auto-rows-min
          "
        >
          {componentsArray.map((config: CanvasComponentConfig, index: number) => {
            const key = config.id ?? `comp-${index}`;
            const Component = ComponentMap[config.type] as
              | React.ComponentType<any>
              | undefined;

            // Card wrapper ensures consistent padding + full stretch
            return (
              <div
                key={key}
                className="w-full h-full flex flex-col rounded-2xl overflow-hidden"
                // give a small min height so cards are visible even with little content
                style={{ minHeight: 220 }}
              >
                {/* If component not found, show a placeholder card */}
                {!Component ? (
                  <div className="flex-1 bg-red-900/20 border border-red-700 rounded-lg p-4">
                    <p className="text-red-400 font-semibold">
                      ⚠️ Component Not Found
                    </p>
                    <p className="text-red-300 text-sm mt-1">
                      "{config.type}" is not registered in ComponentMap
                    </p>
                    <p className="text-red-400 text-xs mt-2">Index: {index}</p>
                  </div>
                ) : (
                  // Inner wrapper gives the component full space to render and allows
                  // component-internal layout to behave responsively.
                  <div className="flex-1 w-full">
                    {/* Spread config.data; also provide className so components can accept it */}
                    <Component {...(config.data ?? {})} className="w-full h-full" />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {componentsArray.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No components in this version</p>
          </div>
        )}
      </div>
    </main>
  );
};
