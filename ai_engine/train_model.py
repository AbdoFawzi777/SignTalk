"""
SignTalk - AI Engine: Model Training & Evaluation Suite (Phase 2)
Author: SignTalk Lead AI Engineer
Description: Trains a lightweight Bidirectional LSTM model on 30-frame x 126-feature
             hand landmark sequences, generates classification metrics, confusion 
             matrices, accuracy curves, and exports the trained Keras model.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data')
DEFAULT_ACTIONS = ['hello', 'thanks', 'help', 'doctor', 'water', 'food', 'police', 'yes', 'no', 'emergency']
SEQUENCE_LENGTH = 30
FEATURE_DIM = 126

def ensure_dataset_exists():
    """
    Checks if real landmark dataset exists in 'data/'. If missing or empty,
    generates synthetic sample sequences so training can be tested out-of-the-box.
    """
    if not os.path.exists(DATA_PATH) or len(os.listdir(DATA_PATH)) == 0:
        print("[!] Real dataset not found in 'ai_engine/data/'. Generating synthetic keypoint dataset for demonstration...")
        for action in DEFAULT_ACTIONS:
            for sequence in range(30):
                seq_dir = os.path.join(DATA_PATH, action, str(sequence))
                os.makedirs(seq_dir, exist_ok=True)
                base = np.random.uniform(-0.5, 0.5, size=(FEATURE_DIM,))
                for frame_num in range(SEQUENCE_LENGTH):
                    noise = np.random.normal(0, 0.02, size=(FEATURE_DIM,))
                    keypoints = base + (frame_num / SEQUENCE_LENGTH) * 0.15 + noise
                    np.save(os.path.join(seq_dir, f"{frame_num}.npy"), keypoints)
        print("[+] Synthetic dataset generated successfully.")

def load_data():
    """
    Loads .npy sequence files from dataset directory.
    Returns feature matrix X (N, 30, 126) and one-hot labels y (N, num_classes).
    """
    ensure_dataset_exists()
    
    actions = [d for d in os.listdir(DATA_PATH) if os.path.isdir(os.path.join(DATA_PATH, d))]
    actions.sort()
    label_map = {label: num for num, label in enumerate(actions)}

    sequences, labels = [], []

    print(f"[+] Loading gesture keypoint data for {len(actions)} classes: {actions}")

    for action in actions:
        action_dir = os.path.join(DATA_PATH, action)
        seq_folders = [f for f in os.listdir(action_dir) if os.path.isdir(os.path.join(action_dir, f))]

        for seq in seq_folders:
            seq_path = os.path.join(action_dir, seq)
            window = []
            valid_seq = True
            
            for frame_num in range(SEQUENCE_LENGTH):
                frame_path = os.path.join(seq_path, f"{frame_num}.npy")
                if os.path.exists(frame_path):
                    res = np.load(frame_path)
                    window.append(res)
                else:
                    valid_seq = False
                    break

            if valid_seq and len(window) == SEQUENCE_LENGTH:
                sequences.append(window)
                labels.append(label_map[action])

    X = np.array(sequences, dtype=np.float32)
    y = tf.keras.utils.to_categorical(labels, num_classes=len(actions)).astype(np.float32)

    return X, y, actions

def build_bilstm_model(input_shape, num_classes):
    """
    Builds an optimized Bidirectional LSTM architecture for mobile TFLite conversion.
    Input Shape: (30, 126)
    """
    model = Sequential([
        # Layer 1: Bidirectional LSTM
        Bidirectional(LSTM(64, return_sequences=True, activation='tanh'), input_shape=input_shape),
        Dropout(0.3),
        BatchNormalization(),

        # Layer 2: Second Bidirectional LSTM
        Bidirectional(LSTM(32, return_sequences=False, activation='tanh')),
        Dropout(0.3),
        BatchNormalization(),

        # Fully Connected Classification Head
        Dense(64, activation='relu'),
        Dense(32, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])

    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['categorical_accuracy']
    )
    return model

def plot_and_save_metrics(history, y_true, y_pred, actions):
    """Generates and saves training curves and confusion matrix plot."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # Accuracy Plot
    ax1.plot(history.history['categorical_accuracy'], label='Train Accuracy', color='#6C5CE7', linewidth=2)
    ax1.plot(history.history['val_categorical_accuracy'], label='Val Accuracy', color='#00CEC9', linewidth=2)
    ax1.set_title('SignTalk Model Accuracy Curve')
    ax1.set_xlabel('Epochs')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Purples', xticklabels=actions, yticklabels=actions, ax=ax2)
    ax2.set_title('Gesture Classification Confusion Matrix')
    ax2.set_xlabel('Predicted Label')
    ax2.set_ylabel('True Label')

    plt.tight_layout()
    metrics_path = os.path.join(BASE_DIR, 'training_metrics.png')
    plt.savefig(metrics_path, dpi=300)
    print(f"[+] Metrics plots saved to '{metrics_path}'")

def train():
    print("=======================================================")
    print("      SignTalk Phase 2: AI Neural Network Training     ")
    print("=======================================================")

    X, y, actions = load_data()
    print(f"[+] Feature Matrix Shape X: {X.shape} | Labels Shape y: {y.shape}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    model = build_bilstm_model((SEQUENCE_LENGTH, FEATURE_DIM), len(actions))
    model.summary()

    callbacks = [
        EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1),
        ModelCheckpoint(os.path.join(BASE_DIR, 'best_signtalk_model.keras'), monitor='val_categorical_accuracy', save_best_only=True, verbose=1)
    ]

    print("\n[+] Starting Model Training...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=60,
        batch_size=16,
        callbacks=callbacks
    )

    # Evaluate Model
    y_pred_prob = model.predict(X_test)
    y_true = np.argmax(y_test, axis=1)
    y_pred = np.argmax(y_pred_prob, axis=1)

    acc = accuracy_score(y_true, y_pred)
    print(f"\n[+] Final Test Accuracy: {acc * 100:.2f}%\n")
    print("Classification Report:\n", classification_report(y_true, y_pred, target_names=actions))

    # Save Labels Text File
    labels_file = os.path.join(BASE_DIR, 'labels.txt')
    with open(labels_file, 'w', encoding='utf-8') as f:
        for action in actions:
            f.write(f"{action}\n")
    print(f"[+] Saved gesture labels to '{labels_file}'")

    # Save Keras Model
    keras_save_path = os.path.join(BASE_DIR, 'signtalk_model.keras')
    model.save(keras_save_path)
    print(f"[+] Keras model saved to '{keras_save_path}'")

    # Plot & Save Metrics
    try:
        plot_and_save_metrics(history, y_true, y_pred, actions)
    except Exception as e:
        print(f"[!] Plotting warning: {e}")

if __name__ == '__main__':
    train()
