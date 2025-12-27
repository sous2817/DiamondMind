import React from 'react';
import { StyleSheet, View } from 'react-native';
import Svg, { Line, Circle } from 'react-native-svg';

// MediaPipe Pose Connections (defines which IDs connect to form bones)
const POSE_CONNECTIONS = [
  // The "Upper Power Box" (Shoulders & Arms)
  [11, 12], [11, 13], [13, 15], [12, 14], [14, 16], 
  // The "Core Stack" (Shoulders to Hips)
  [11, 23], [12, 24], 
  // The "Lower Power Box" (Hips)
  [23, 24], 
  // The "Drive Leg" and "Lead Leg"
  [23, 25], [25, 27], [27, 31], // Left side
  [24, 26], [26, 28], [28, 32]  // Right side
];
const SkeletonOverlay = ({ landmarks, width, height }) => {
  if (!landmarks || landmarks.length === 0) return null;

  return (
    <View style={[StyleSheet.absoluteFill, { width, height }]}>
      <Svg height="100%" width="100%" viewBox={`0 0 ${width} ${height}`}>
        {/* Draw Bones */}
        {POSE_CONNECTIONS.map(([startIdx, endIdx], index) => {
          const start = landmarks[startIdx];
          const end = landmarks[endIdx];

          if (!start || !end || start.visibility < 0.5 || end.visibility < 0.5) return null;

          return (
            <Line
              key={`bone-${index}`}
              x1={start.x * width}
              y1={start.y * height}
              x2={end.x * width}
              y2={end.y * height}
              stroke="#00FF00" // Neon Green for visibility
              strokeWidth="3"
            />
          );
        })}

        {/* Draw Joints */}
        {landmarks.map((lm, index) => {
          if (lm.visibility < 0.5) return null;
          return (
            <Circle
              key={`joint-${index}`}
              cx={lm.x * width}
              cy={lm.y * height}
              r="4"
              fill="#FF3B30" // Red joints
            />
          );
        })}
      </Svg>
    </View>
  );
};

export default SkeletonOverlay;