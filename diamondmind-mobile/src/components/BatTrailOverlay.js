import React from 'react';
import { View, StyleSheet } from 'react-native';
import Svg, { Polyline, Circle } from 'react-native-svg';

const BatTrailOverlay = ({
    frames,
    currentFrameIndex,
    videoWidth,
    videoHeight,
    containerWidth,
    containerHeight
}) => {
    if (!frames || !frames.length || !videoWidth || !videoHeight || !containerWidth || !containerHeight) {
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

    // Extract bat positions from frames (up to current frame for progressive trail)
    const batPositions = frames
        .slice(0, currentFrameIndex + 1)
        .map(frame => frame.bat_position)
        .filter(pos => pos !== null && pos !== undefined);

    if (batPositions.length < 2) {
        // Need at least 2 points to draw a trail
        return null;
    }

    // Convert normalized coordinates to screen pixels
    const points = batPositions.map(pos => {
        const x = offsetX + (pos.x * displayWidth);
        const y = offsetY + (pos.y * displayHeight);
        return `${x},${y}`;
    }).join(' ');

    // Get current bat position for highlighting
    const currentBatPos = frames[currentFrameIndex]?.bat_position;

    return (
        <View style={StyleSheet.absoluteFill} pointerEvents="none">
            <Svg
                height="100%"
                width="100%"
                viewBox={`0 0 ${containerWidth} ${containerHeight}`}
            >
                {/* Bat trail (polyline) */}
                <Polyline
                    points={points}
                    fill="none"
                    stroke="#FFD700"
                    strokeWidth="3"
                    strokeOpacity="0.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                />

                {/* Current bat position (highlighted circle) */}
                {currentBatPos && (
                    <Circle
                        cx={offsetX + (currentBatPos.x * displayWidth)}
                        cy={offsetY + (currentBatPos.y * displayHeight)}
                        r="8"
                        fill="#FFD700"
                        opacity="1"
                    />
                )}
            </Svg>
        </View>
    );
};

// Memoize to prevent unnecessary re-renders
export default React.memo(BatTrailOverlay, (prevProps, nextProps) => {
    return prevProps.currentFrameIndex === nextProps.currentFrameIndex &&
        prevProps.containerWidth === nextProps.containerWidth &&
        prevProps.containerHeight === nextProps.containerHeight;
});
