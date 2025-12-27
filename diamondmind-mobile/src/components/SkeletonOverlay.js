import React from 'react';
import { StyleSheet, View } from 'react-native';
import Svg, { Line, Circle } from 'react-native-svg';

const POSE_CONNECTIONS = [
    [11, 12], [11, 13], [13, 15], [12, 14], [14, 16], [11, 23], [12, 24],
    [23, 24], [23, 25], [25, 27], [27, 31], [24, 26], [26, 28], [28, 32]
];

const SkeletonOverlay = ({ landmarks, width, height, naturalSize }) => {
    // 1. Strict Guard: Stop if no landmarks or no UI container size
    if (!landmarks || landmarks.length === 0 || width === 0 || height === 0) {
        return null;
    }

    // 2. Safe Fallback: If naturalSize isn't ready, use container width/height
    const vWidth = naturalSize?.width || width;
    const vHeight = naturalSize?.height || height;

    // 3. Math Section: Scale to fit "contain" mode
    const scale = Math.min(width / vWidth, height / vHeight);
    const actualVideoWidth = vWidth * scale;
    const actualVideoHeight = vHeight * scale;

    // 4. Offset for letterboxing (black bars)
    const offsetX = (width - actualVideoWidth) / 2;
    const offsetY = (height - actualVideoHeight) / 2;

    return (
        <View style={StyleSheet.absoluteFill} pointerEvents="none">
            <Svg height={height} width={width}>
                {/* Draw Bones (Lines) */}
                {POSE_CONNECTIONS.map(([startIdx, endIdx], index) => {
                    const start = landmarks[startIdx];
                    const end = landmarks[endIdx];

                    // Skip if landmarks are missing or visibility is too low
                    if (!start || !end || (start.visibility < 0.5) || (end.visibility < 0.5)) return null;

                    return (
                        <Line
                            key={`bone-${index}`}
                            x1={start.x * actualVideoWidth + offsetX}
                            y1={start.y * actualVideoHeight + offsetY}
                            x2={end.x * actualVideoWidth + offsetX}
                            y2={end.y * actualVideoHeight + offsetY}
                            stroke="#00FF00"
                            strokeWidth="3"
                        />
                    );
                })}

                {/* Draw Joints (Circles) */}
                {landmarks.map((lm, index) => {
                    if (!lm || lm.visibility < 0.5) return null;
                    return (
                        <Circle
                            key={`joint-${index}`}
                            cx={lm.x * actualVideoWidth + offsetX}
                            cy={lm.y * actualVideoHeight + offsetY}
                            r="4"
                            fill="#FF3B30"
                        />
                    );
                })}
            </Svg>
        </View>
    );
};

export default SkeletonOverlay;