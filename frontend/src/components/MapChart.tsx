import React, { useMemo } from 'react';
import { ComposableMap, Geographies, Geography, Marker } from 'react-simple-maps';

const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

interface MapChartProps {
  markers?: { name: string; coordinates: [number, number]; value: number }[];
}

export const MapChart: React.FC<MapChartProps> = ({ markers = [] }) => {
  return (
    <ComposableMap projection="geoMercator" projectionConfig={{ scale: 120 }}>
      <Geographies geography={geoUrl}>
        {({ geographies }) =>
          geographies.map((geo) => (
            <Geography
              key={geo.rsmKey}
              geography={geo}
              fill="#ffffff"
              stroke="#e2e8f0"
              strokeWidth={0.5}
              style={{
                default: { outline: "none" },
                hover: { fill: "#1e293b", outline: "none" },
                pressed: { outline: "none" },
              }}
            />
          ))
        }
      </Geographies>
      {markers.map(({ name, coordinates, value }, i) => (
        <Marker key={i} coordinates={coordinates}>
          <circle r={Math.max(2, Math.min(value / 10, 10))} fill="#0369a1" opacity={0.7} />
          <title>{name}</title>
        </Marker>
      ))}
    </ComposableMap>
  );
};
