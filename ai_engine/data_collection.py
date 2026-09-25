"""
SignTalk - AI Engine: Interactive Keypoint Data Collection Suite
Author: SignTalk Lead AI Engineer
Description: Interactive OpenCV + MediaPipe Hands 3D keypoint recording tool for 
             collecting time-series sign gesture sequences saved as .npy files.

Keyboard Shortcuts:
  [SPACE] - Start recording 30-frame sequence batch for current action
  [N]     - Enter/Change Action Name
  [P]     - Toggle Pause/Standby
  [C]     - Clear data for current action
  [Q]     - Quit safely
"""

import os
import sys
import time
import cv2
import numpy as np
import mediapipe as mp

# --- CONFIGURATION & CONSTANTS ---
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DEFAULT_ACTIONS = ['hello', 'thanks', 'help', 'doctor', 'water', 'food', 'police', 'yes', 'no', 'emergency']
SEQUENCE_LENGTH = 30    # 30 frames per gesture (~1 second motion at 30 FPS)
DEFAULT_NO_SEQUENCES = 30 # Number of recorded video samples per action
FEATURE_DIM = 126       # 21 points x 3 coords (x,y,z) x 2 hands = 126

class KeypointCollector:
    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = data_dir
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.current_action = DEFAULT_ACTIONS[0]
        self.sequence_count = DEFAULT_NO_SEQUENCES
        self.is_recording = False
        self.is_paused = False

        # Ensure root data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

    def extract_landmarks(self, results):
        """
        Extracts 21 3D coordinates (x, y, z) for Left and Right hands.
        Returns a normalized 1D numpy array of length 126.
        """
        left_hand = np.zeros(21 * 3)
        right_hand = np.zeros(21 * 3)

        if results.left_hand_landmarks:
            lh = np.array([[lm.x, lm.y, lm.z] for lm in results.left_hand_landmarks.landmark]).flatten()
            left_hand = lh

        if results.right_hand_landmarks:
            rh = np.array([[lm.x, lm.y, lm.z] for lm in results.right_hand_landmarks.landmark]).flatten()
            right_hand = rh

        return np.concatenate([left_hand, right_hand])

    def setup_action_dirs(self, action_name):
        """Creates sequence subdirectories for a specific action gesture."""
        action_path = os.path.join(self.data_dir, action_name)
        os.makedirs(action_path, exist_ok=True)
        
        # Check existing sequences to continue recording without overwriting
        existing_seqs = [d for d in os.listdir(action_path) if os.path.isdir(os.path.join(action_path, d))]
        return action_path, len(existing_seqs)

    def draw_ui_overlay(self, image, fps, current_seq, current_frame, left_detected, right_detected):
        """Renders rich HUD, FPS, status badges, and instructions on the video frame."""
        h, w, _ = image.shape

        # 1. Dark HUD Top Bar
        cv2.rectangle(image, (0, 0), (w, 85), (20, 20, 30), -1)
        cv2.line(image, (0, 85), (w, 85), (0, 255, 200), 2)

        # Action Title & FPS
        cv2.putText(image, f"SignTalk Collector | Action: '{self.current_action.upper()}'", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, f"FPS: {fps:.1f}", (w - 120, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

        # Hand Detection Badges
        lh_color = (0, 255, 0) if left_detected else (100, 100, 100)
        rh_color = (0, 255, 0) if right_detected else (100, 100, 100)
        cv2.putText(image, "L-Hand", (15, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, lh_color, 2, cv2.LINE_AA)
        cv2.putText(image, "R-Hand", (90, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, rh_color, 2, cv2.LINE_AA)

        # Recording Status & Sequence Counter
        if self.is_recording:
            status_text = f"REC: Sequence {current_seq}/{self.sequence_count} [Frame {current_frame + 1}/{SEQUENCE_LENGTH}]"
            cv2.putText(image, status_text, (200, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2, cv2.LINE_AA)
            # Progress Bar
            progress_w = int((current_frame + 1) / SEQUENCE_LENGTH * (w - 400))
            cv2.rectangle(image, (380, 72), (380 + progress_w, 78), (0, 0, 255), -1)
        else:
            cv2.putText(image, "STANDBY - Press [SPACE] to Record Sequences", (200, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2, cv2.LINE_AA)

        # 2. Bottom Shortcut Controls Bar
        cv2.rectangle(image, (0, h - 35), (w, h), (15, 15, 20), -1)
        cv2.putText(image, "[SPACE] Record | [N] Action Name | [P] Pause | [Q] Quit", (15, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)

    def draw_styled_landmarks(self, image, results):
        """Draws MediaPipe hand landmark joints and connections."""
        if results.left_hand_landmarks:
            self.mp_drawing.draw_landmarks(
                image,
                results.left_hand_landmarks,
                self.mp_holistic.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
        if results.right_hand_landmarks:
            self.mp_drawing.draw_landmarks(
                image,
                results.right_hand_landmarks,
                self.mp_holistic.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )

    def start_collection_loop(self, camera_index=0):
        """Main OpenCV camera capture and event loop."""
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"[-] Error: Could not open camera at index {camera_index}.")
            return

        print(f"\n=======================================================")
        print(f"       SignTalk Interactive Keypoint Collector        ")
        print(f"=======================================================")
        print(f"Target Data Directory: '{os.path.abspath(self.data_dir)}'")
        print(f"Default Action: '{self.current_action}'")
        print(f"Press [SPACE] in the camera window to start recording.\n")

        prev_frame_time = time.time()

        with self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("[-] Frame capture failed. Exiting camera loop.")
                    break

                # FPS Calculation
                new_frame_time = time.time()
                fps = 1 / (new_frame_time - prev_frame_time + 1e-6)
                prev_frame_time = new_frame_time

                # Flip frame horizontally for natural selfie feedback
                frame = cv2.flip(frame, 1)

                # MediaPipe Processing
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = holistic.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                left_detected = results.left_hand_landmarks is not None
                right_detected = results.right_hand_landmarks is not None

                # Render Visual Mesh
                self.draw_styled_landmarks(image, results)
                self.draw_ui_overlay(image, fps, 0, 0, left_detected, right_detected)

                cv2.imshow('SignTalk - Interactive Keypoint Data Collector', image)

                key = cv2.waitKey(10) & 0xFF
                if key == ord('q'):
                    print("[!] User requested quit.")
                    break
                elif key == ord('n'):
                    new_name = input("\n[>] Enter new Action/Gesture Name (e.g. 'hospital'): ").strip().lower()
                    if new_name:
                        self.current_action = new_name
                        print(f"[+] Action updated to: '{self.current_action}'")
                elif key == 32: # SPACEBAR
                    self.record_sequences_batch(cap, holistic)

        cap.release()
        cv2.destroyAllWindows()
        print("[+] Camera released. Session closed successfully.")

    def record_sequences_batch(self, cap, holistic):
        """Records a batch of sequences for the active gesture."""
        self.is_recording = True
        action_path, existing_count = self.setup_action_dirs(self.current_action)

        print(f"\n[+] Starting Recording Batch for Action: '{self.current_action.upper()}'")
        print(f"[+] Output Folder: '{action_path}'")

        for sequence in range(existing_count, existing_count + self.sequence_count):
            seq_dir = os.path.join(action_path, str(sequence))
            os.makedirs(seq_dir, exist_ok=True)

            for frame_num in range(SEQUENCE_LENGTH):
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = holistic.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                left_detected = results.left_hand_landmarks is not None
                right_detected = results.right_hand_landmarks is not None

                self.draw_styled_landmarks(image, results)

                # Inter-sequence prompt on first frame
                if frame_num == 0:
                    cv2.putText(image, 'GET READY FOR NEXT SEQUENCE...', (100, 250),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
                    self.draw_ui_overlay(image, 30.0, sequence + 1, frame_num, left_detected, right_detected)
                    cv2.imshow('SignTalk - Interactive Keypoint Data Collector', image)
                    cv2.waitKey(1200) # Short prep delay
                else:
                    self.draw_ui_overlay(image, 30.0, sequence + 1, frame_num, left_detected, right_detected)
                    cv2.imshow('SignTalk - Interactive Keypoint Data Collector', image)

                # Save Keypoints Vector
                keypoints = self.extract_landmarks(results)
                npy_path = os.path.join(seq_dir, f"{frame_num}.npy")
                np.save(npy_path, keypoints)

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    self.is_recording = False
                    print("[!] Sequence recording aborted.")
                    return

        self.is_recording = False
        print(f"[+] Recording Batch Complete for '{self.current_action.upper()}'! Saved {self.sequence_count} sequences.")

if __name__ == '__main__':
    collector = KeypointCollector()
    collector.start_collection_loop()
