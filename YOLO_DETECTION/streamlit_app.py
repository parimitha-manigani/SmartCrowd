import streamlit as st
import threading
import pickle
import time
import sys

# Import functions from your project
from api import apiWorker
from tracker import getJson
from main import yoloWorker

# Append necessary paths
sys.path.append("C:/Users/Chinna/Desktop/final year project/project2/YOLO_DETECTION")

# Global variables
yolo_thread = None
api_thread = None
stop_threads = False

# Function to start YOLO detection
def start_yolo(parameterlist):
    global yolo_thread, api_thread, stop_threads
    stop_threads = False
    st.session_state["detection_status"] = "running"

    # Save parameters to file for YOLO
    with open('settings.data', 'wb') as filehandle:
        pickle.dump(parameterlist, filehandle)

    # Start YOLO and API worker threads
    yolo_thread = threading.Thread(target=yoloWorker, args=(parameterlist,))
    api_thread = threading.Thread(target=apiWorker)

    api_thread.setDaemon(True)
    api_thread.start()
    yolo_thread.start()

# Function to stop YOLO detection
def stop_yolo():
    global stop_threads
    stop_threads = True
    st.session_state["detection_status"] = "stopped"
    st.write("Stopping detection...")
    time.sleep(2)  # Allow threads to exit cleanly

# Streamlit UI
st.title("YOLO Object Detection Interface")
st.subheader("Configure Detection Parameters")

# Detection Options
st.sidebar.header("Detection Options")
visualizeBBoxes = st.sidebar.checkbox("Draw Boundary Boxes", value=True)
visualizerCenters = st.sidebar.checkbox("Visualizer Centers", value=True)
calculateDirection = st.sidebar.checkbox("Calculate Direction", value=True)
calculateSpeed = st.sidebar.checkbox("Calculate Speed", value=True)
calculatePeopleCount = st.sidebar.checkbox("Calculate People Count", value=True)
calculateTotalPeopleCount = st.sidebar.checkbox("Calculate Total People Count", value=True)
calculateLineCross = st.sidebar.checkbox("Calculate Line Cross", value=False)

# Detection Classes
st.sidebar.header("Detection Classes")
classes_input = st.sidebar.text_input("Enter detection classes (comma-separated)", "person,car")

# Video Source
st.sidebar.header("Video Source")
video_source_option = st.sidebar.radio(
    "Select Video Source",
    ["Default Camera", "External Camera", "Custom Source URL"],
)

if video_source_option == "Default Camera":
    video_source = "0"
elif video_source_option == "External Camera":
    video_source = "1"
else:
    video_source = st.sidebar.text_input("Enter video source URL", "http://root:root@192.168.70.52/mjpg/1/video.mjpg")

# Save Parameters and Start Detection
col1, col2 = st.columns(2)
if "detection_status" not in st.session_state:
    st.session_state["detection_status"] = "stopped"

if col1.button("Start Detection"):
    if st.session_state["detection_status"] == "running":
        st.warning("Detection is already running.")
    else:
        # Build parameter list dynamically
        parameterlist = [
            visualizeBBoxes,           # Draw Boundary Boxes
            visualizerCenters,         # Visualize Centers
            calculateDirection,        # Calculate Direction
            calculateSpeed,            # Calculate Speed
            calculatePeopleCount,      # Calculate People Count
            calculateTotalPeopleCount, # Calculate Total People Count
            [classes_input.split(",")], # Classes to Detect
            calculateLineCross,        # Calculate Line Cross
            video_source               # Video Source
        ]
        start_yolo(parameterlist)
        st.success("YOLO Detection started!")

if col2.button("Stop Detection"):
    if st.session_state["detection_status"] == "stopped":
        st.warning("Detection is not running.")
    else:
        stop_yolo()
        st.success("YOLO Detection stopped.")

# Results Display Section
st.header("Live Detection Results")
if st.session_state["detection_status"] == "running":
    placeholder = st.empty()

    # Dynamically fetch and display results
    while st.session_state["detection_status"] == "running":
        result = getJson()
        placeholder.json(result)
        time.sleep(5)
else:
    st.info("Start detection to see results.")



