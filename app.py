import streamlit as st
import cv2
import sys
import os
import pandas as pd
from PIL import Image
import numpy as np
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from detection.detector import SurveillanceDetector
from alerts.alert_manager import AlertManager
from database.database import DetectionDatabase

# ─── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Surveillance System",
    page_icon="🎥",
    layout="wide"
)

# ─── HEADER ───────────────────────────────────────────────────
import config

st.title(f"🎥 {config.PROJECT_NAME}")
st.markdown(f"*{config.PROJECT_TITLE}*")

with st.expander("ℹ️ Project Info", expanded=False):
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**University:** {config.UNIVERSITY}")
    col1.markdown(f"**Department:** {config.DEPARTMENT}")
    col2.markdown(f"**Supervisor:** {config.SUPERVISOR}")
    col2.markdown(f"**Version:** {config.VERSION}")
    col3.markdown(f"**Students:**")
    for s in config.STUDENTS:
        col3.markdown(f"- {s['name']} `{s['reg']}`")

st.divider()

# ─── SIDEBAR ──────────────────────────────────────────────────
st.sidebar.header("⚙️ Settings")
confidence = st.sidebar.slider("Detection Confidence", 0.3, 0.9, 0.5, 0.05)
cooldown   = st.sidebar.slider("Alert Cooldown (seconds)", 3, 30, 5)
enable_alarm = st.sidebar.toggle("🔔 Enable Alarm Sound", value=True)

st.sidebar.divider()
st.sidebar.markdown("**ROI Zone (Restricted Area)**")
st.sidebar.markdown("*Percentage of frame width/height*")
roi_x1 = st.sidebar.slider("Zone Left %",   0,  50, 20)
roi_y1 = st.sidebar.slider("Zone Top %",    0,  50, 20)
roi_x2 = st.sidebar.slider("Zone Right %", 50, 100, 80)
roi_y2 = st.sidebar.slider("Zone Bottom %",50, 100, 80)

# ─── TABS ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📹 Live Monitor",
    "🚨 Alert Log",
    "📸 Snapshots",
    "📊 Statistics"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — LIVE MONITOR
# ══════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([3, 1])

    with col2:
        st.markdown("### Controls")
        source = st.radio("Video Source", ["Webcam", "Upload Video"])

        if source == "Upload Video":
            uploaded = st.file_uploader("Upload a video", type=["mp4","avi","mov"])

        start_btn = st.button("▶ Start Detection", type="primary", use_container_width=True)
        stop_btn  = st.button("⏹ Stop",            use_container_width=True)

        st.divider()
        status_box    = st.empty()
        detection_box = st.empty()
        alert_box     = st.empty()

    with col1:
        st.markdown("### Live Feed")
        frame_placeholder = st.empty()

    # ── DETECTION LOOP ────────────────────────────────────────
    if start_btn:
        # Initialize modules
        detector  = SurveillanceDetector(confidence=confidence)
        alert_mgr = AlertManager(cooldown_sec=cooldown)
        db        = DetectionDatabase()

        # Open video source
        if source == "Webcam":
            cap = cv2.VideoCapture(0)
        else:
            if uploaded is not None:
                # Save uploaded file temporarily
                tmp_path = "data/test_videos/uploaded.mp4"
                with open(tmp_path, "wb") as f:
                    f.write(uploaded.read())
                cap = cv2.VideoCapture(tmp_path)
            else:
                st.warning("Please upload a video file first.")
                st.stop()

        if not cap.isOpened():
            st.error("❌ Could not open video source. Check your camera or file.")
            st.stop()

        status_box.success("🟢 Detection Running")
        frame_count = 0
        SKIP = 3  # process every 3rd frame for speed

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                status_box.info("✅ Video ended.")
                break

            frame_count += 1

            # Calculate ROI zone based on frame dimensions
            h, w = frame.shape[:2]
            zone = (
                int(w * roi_x1 / 100), int(h * roi_y1 / 100),
                int(w * roi_x2 / 100), int(h * roi_y2 / 100)
            )

            # Run detection every SKIP frames
            if frame_count % SKIP == 0:
                results  = detector.detect(frame)
                boxes    = detector.get_boxes(results)
                in_zone  = [b for b in boxes if detector.is_in_zone(b, zone)]
                triggered = len(in_zone) > 0

                # Draw zone and boxes
                frame = detector.draw_zone(frame, zone, triggered)
                frame = detector.draw_boxes(frame, boxes, alert=triggered)

                # Trigger alert if someone is in restricted zone
                if triggered and enable_alarm:
                    best_conf = max(b['confidence'] for b in in_zone)
                    event = alert_mgr.trigger_alert(frame, "Zone A", best_conf)
                    if event:
                        db.log_event(
                            event['timestamp'],
                            event['confidence'],
                            event['zone'],
                            event['snapshot_path']
                        )
                        alert_box.error(f"🚨 ALERT! Intruder in {event['zone']}")

                # Update sidebar stats
                detection_box.metric("Persons Detected", len(boxes))

            # Add timestamp to frame
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, ts, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Display frame (convert BGR to RGB for Streamlit)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

            # Check stop button
            if stop_btn:
                break

        cap.release()
        status_box.warning("⏹ Detection Stopped")

# ══════════════════════════════════════════════════════════════
# TAB 2 — ALERT LOG
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Detection Event Log")
    db = DetectionDatabase()
    df = db.get_all_events()

    if len(df) > 0:
        st.metric("Total Alerts", len(df))
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False)
        st.download_button("⬇ Export CSV", csv, "events.csv", "text/csv")
    else:
        st.info("No events logged yet. Start detection to begin.")

# ══════════════════════════════════════════════════════════════
# TAB 3 — SNAPSHOTS
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Alert Snapshots")
    snap_dir = "data/snapshots"

    if os.path.exists(snap_dir):
        snaps = sorted(os.listdir(snap_dir))
        if snaps:
            st.metric("Total Snapshots", len(snaps))
            # Show latest 12
            cols = st.columns(3)
            for i, snap in enumerate(reversed(snaps[-12:])):
                path = os.path.join(snap_dir, snap)
                cols[i % 3].image(path, caption=snap, use_container_width=True)
        else:
            st.info("No snapshots yet.")
    else:
        st.info("Snapshots folder not found.")

# ══════════════════════════════════════════════════════════════
# TAB 4 — STATISTICS
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Detection Statistics")
    db3 = DetectionDatabase()
    df3 = db3.get_all_events()

    if len(df3) > 0:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Alerts",      len(df3))
        col2.metric("Avg Confidence",    f"{df3['confidence'].mean():.0%}")
        col3.metric("Unique Zones",      df3['zone'].nunique())

        st.markdown("#### Alerts Per Day")
        df3['date'] = pd.to_datetime(df3['timestamp']).dt.date
        daily = df3.groupby('date').size().reset_index(name='count')
        st.bar_chart(daily.set_index('date'))

        st.markdown("#### Confidence Distribution")
        st.bar_chart(df3['confidence'].value_counts().sort_index())
    else:
        st.info("No data yet. Run detection to see statistics.")