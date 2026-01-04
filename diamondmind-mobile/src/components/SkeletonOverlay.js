import React from 'react';
import { View, StyleSheet, useWindowDimensions } from 'react-native';
import Svg, { Line, Circle } from 'react-native-svg';

const POSE_CONNECTIONS = [
    [11, 12], [11, 13], [13, 15], [12, 14], [14, 16], [11, 23], [12, 24],
    [23, 24], [23, 25], [25, 27], [27, 31], [24, 26], [26, 28], [28, 32]
];

const SkeletonOverlay = ({ landmarks, videoWidth, videoHeight, containerWidth, containerHeight }) => {
    if (!landmarks || !landmarks.length || !videoWidth || !videoHeight || !containerWidth || !containerHeight) {
        return null;
    }

    // Calculate video aspect ratios
    const videoAspect = videoWidth / videoHeight;
    const containerAspect = containerWidth / containerHeight;

    // Calculate the actual video display dimensions when using contentMode="contain"
    let displayWidth, displayHeight, offsetX, offsetY;

    if (videoAspect > containerAspect) {
        // Video is wider - letterbox top/bottom
        displayWidth = containerWidth;
        displayHeight = containerWidth / videoAspect;
        offsetX = 0;
        offsetY = (containerHeight - displayHeight) / 2;
    } else {
        // Video is taller - letterbox left/right
        displayHeight = containerHeight;
        displayWidth = containerHeight * videoAspect;
        offsetX = (containerWidth - displayWidth) / 2;
        offsetY = 0;
    }

    return (
        <View style={StyleSheet.absoluteFill} pointerEvents="none">
            <Svg
                height="100%"
                width="100%"
                viewBox={`0 0 ${containerWidth} ${containerHeight}`}
            >
                {POSE_CONNECTIONS.map(([startIdx, endIdx], index) => {
                    const start = landmarks[startIdx];
                    const end = landmarks[endIdx];
                    if (!start || !end || start.visibility < 0.5 || end.visibility < 0.5) return null;

                    // Transform normalized coordinates (0-1) to actual screen pixels
                    const x1 = offsetX + (start.x * displayWidth);
                    const y1 = offsetY + (start.y * displayHeight);
                    const x2 = offsetX + (end.x * displayWidth);
                    const y2 = offsetY + (end.y * displayHeight);

                    return (
                        <Line
                            key={`bone-${index}`}
                            x1={x1} y1={y1}
                            x2={x2} y2={y2}
                            stroke="#00FF00"
                            strokeWidth="3"
                        />
                    );
                })}

                {landmarks.map((lm, index) => {
                    if (!lm || lm.visibility < 0.5) return null;

                    const cx = offsetX + (lm.x * displayWidth);
                    const cy = offsetY + (lm.y * displayHeight);

                    return (
                        <Circle
                            key={`joint-${index}`}
                            cx={cx} cy={cy}
                            r="6"
                            fill="#FF3B30"
                        />
                    );
                })}
            </Svg>
        </View>
    );
};

// ⚡️ PERFORMANCE FIX: Prevent re-renders when landmarks haven't changed
// This eliminates jitter by only re-rendering when frame data actually updates
export default React.memo(SkeletonOverlay, (prevProps, nextProps) => {
    return prevProps.landmarks === nextProps.landmarks &&
        prevProps.containerWidth === nextProps.containerWidth &&
        prevProps.containerHeight === nextProps.containerHeight;
});