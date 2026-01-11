// src/components/common/Sparkline.tsx
import React from 'react';
import { Box, useTheme } from '@mui/material';

interface SparklineProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  showArea?: boolean;
}

const Sparkline: React.FC<SparklineProps> = ({ 
  data, 
  width = 100, 
  height = 30,
  color,
  showArea = false 
}) => {
  const theme = useTheme();
  const defaultColor = color || theme.palette.primary.main;

  if (!data || data.length === 0) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  const pathD = `M ${points}`;
  const areaPath = `${pathD} L ${width},${height} L 0,${height} Z`;

  return (
    <Box 
      component="svg" 
      width={width} 
      height={height} 
      sx={{ 
        display: 'block',
        overflow: 'visible'
      }}
    >
      {showArea && (
        <path
          d={areaPath}
          fill={defaultColor}
          fillOpacity={0.2}
        />
      )}
      <polyline
        points={points}
        fill="none"
        stroke={defaultColor}
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Box>
  );
};

export default Sparkline;
