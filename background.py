import cv2
import mediapipe as mp
import numpy as np
import sys

mp_selfie_segmentation = mp.solutions.selfie_segmentation

# Check if the correct number of command-line arguments is provided
if len(sys.argv) != 3:
    print("Usage: python script.py video_file background_file")
    sys.exit(1)

# Extract command-line arguments
videoFilePath = sys.argv[1]
backgroundFilePath = sys.argv[2]
outputFilePath = "output_video.mp4"
# Open input video file
print(videoFilePath)
input_video = cv2.VideoCapture(videoFilePath)

# Check if the video file is successfully opened
if not input_video.isOpened():
    print("Error opening video file.")
    exit()

# Get video properties
fps = int(input_video.get(cv2.CAP_PROP_FPS))
width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fsize = (width, height)

# Create VideoWriter object to save the output video
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
output_video = cv2.VideoWriter(outputFilePath, fourcc, fps, fsize)

# Read the scene image
scene = cv2.imread(backgroundFilePath)
scene = cv2.resize(scene, fsize)

# Initialize selfie segmentation model
with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_seg:
    bg_image = scene
    
    while True:
        ret, frame = input_video.read()
        if not ret:
            break

        # Resize the frame
        frame = cv2.resize(frame, fsize)

        # Flip it to look like a selfie camera
        frame = cv2.flip(frame, 1)

        # Get RGB image to pass to selfie segmentation
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        results = selfie_seg.process(rgb)

        # Get the condition from the segmentation mask
        condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.2

        # Apply background change if condition matches
        output_image = np.where(condition, frame, bg_image)

        # Save the processed frame to the output video
        output_video.write(output_image)

    # Release video capture and writer objects
    input_video.release()
    output_video.release()

print('Video processing completed.')
