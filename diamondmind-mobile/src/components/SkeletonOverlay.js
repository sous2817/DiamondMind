import React from 'react';
import { StyleSheet, View } from 'react-native';
import Svg, { Line, Circle } from 'react-native-svg';

const POSE_CONNECTIONS = [
    [11, 12], [11, 13], [13, 15], [12, 14], [14, 16], [11, 23], [12, 24],
    [23, 24], [23, 25], [25, 27], [27, 31], [24, 26], [26, 28], [28, 32]
];

const SkeletonOverlay = ({ landmarks, width, height, naturalSize }) => {
    //if (!landmarks || !naturalSize || width === 0 || height === 0) return null;
    if (!landmarks || width === 0 || height === 0) return null;
    // --- THE MATH SECTION ---
    // 1. Calculate how the video is being scaled to fit the "contain" mode
    const scale = Math.min(width / naturalSize.width, height / naturalSize.height);

    // 2. Calculate the actual width/height of the drawn video
    const actualVideoWidth = naturalSize.width * scale;
    const actualVideoHeight = naturalSize.height * scale;

    // 3. Calculate the "Black Bar" offsets (Letterboxing)
    const offsetX = (width - actualVideoWidth) / 2;
    const offsetY = (height - actualVideoHeight) / 2;

    return (
        <View style={StyleSheet.absoluteFill} pointerEvents="none">
            <Svg height={height} width={width}>
                {/* Draw Bones */}
                {POSE_CONNECTIONS.map(([startIdx, endIdx], index) => {
                    const start = landmarks[startIdx];
                    const end = landmarks[endIdx];

                    if (!start || !end || start.visibility < 0.5 || end.visibility < 0.5) return null;

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

                {/* Draw Joints */}
                {landmarks.map((lm, index) => {
                    if (lm.visibility < 0.5) return null;
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