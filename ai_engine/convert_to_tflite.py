"""
SignTalk - AI Engine: TFLite Model Converter & Quantization Tool (Phase 2)
Author: SignTalk Lead AI Engineer
Description: Converts trained Keras model into optimized Float16 and INT8 TensorFlow Lite (.tflite) 
             models and automatically deploys them directly into the Flutter mobile app assets folder.
"""

import os
import shutil
import numpy as np
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KERAS_MODEL_PATH = os.path.join(BASE_DIR, 'signtalk_model.keras')
LABELS_FILE_PATH = os.path.join(BASE_DIR, 'labels.txt')

# Flutter Mobile App Target Asset Paths
MOBILE_ASSETS_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'mobile_app', 'assets'))
MOBILE_MODEL_DIR = os.path.join(MOBILE_ASSETS_DIR, 'models')
TARGET_TFLITE_PATH = os.path.join(MOBILE_MODEL_DIR, 'signtalk_model.tflite')
TARGET_LABELS_PATH = os.path.join(MOBILE_ASSETS_DIR, 'labels.txt')

def representative_data_gen():
    """Generates sample keypoint data sequence for INT8 integer quantization calibration."""
    for _ in range(100):
        sample = np.random.uniform(-1.0, 1.0, size=(1, 30, 126)).astype(np.float32)
        yield [sample]

def convert_and_deploy_tflite(quant_mode='float16'):
    """
    Converts Keras model to quantized TFLite format and deploys to mobile assets.
    Modes: 'float16', 'int8', 'dynamic'
    """
    if not os.path.exists(KERAS_MODEL_PATH):
        print(f"[-] Error: Keras model file not found at '{KERAS_MODEL_PATH}'. Run train_model.py first.")
        return

    print(f"[+] Loading Keras model from '{KERAS_MODEL_PATH}'...")
    model = tf.keras.models.load_model(KERAS_MODEL_PATH)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # Select TF Ops for compatibility with LSTM operations
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,
        tf.lite.OpsSet.SELECT_TF_OPS
    ]
    converter._experimental_lower_tensor_list_ops = False

    if quant_mode == 'float16':
        print("[+] Applying Float16 Quantization...")
        converter.target_spec.supported_types = [tf.float16]
    elif quant_mode == 'int8':
        print("[+] Applying Full INT8 Integer Quantization...")
        converter.representative_dataset = representative_data_gen
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS_INT8,
            tf.lite.OpsSet.SELECT_TF_OPS
        ]
        converter.inference_input_type = tf.float32
        converter.inference_output_type = tf.float32

    print("[+] Converting model to TFLite format...")
    tflite_binary = converter.convert()

    # Create mobile assets directories
    os.makedirs(MOBILE_MODEL_DIR, exist_ok=True)

    # Save to local ai_engine directory
    local_tflite = os.path.join(BASE_DIR, 'signtalk_model.tflite')
    with open(local_tflite, 'wb') as f:
        f.write(tflite_binary)

    # Deploy directly to mobile app assets folder
    with open(TARGET_TFLITE_PATH, 'wb') as f:
        f.write(tflite_binary)

    file_size_kb = os.path.getsize(TARGET_TFLITE_PATH) / 1024.0
    file_size_mb = file_size_kb / 1024.0

    print(f"[+] Success! TFLite Model Saved & Deployed to Mobile App:")
    print(f"    - Target Path: '{TARGET_TFLITE_PATH}'")
    print(f"    - Model Size : {file_size_kb:.2f} KB ({file_size_mb:.2f} MB)")

    # Copy labels.txt to mobile assets
    if os.path.exists(LABELS_FILE_PATH):
        shutil.copy(LABELS_FILE_PATH, TARGET_LABELS_PATH)
        print(f"[+] Gesture Labels deployed to '{TARGET_LABELS_PATH}'")

if __name__ == '__main__':
    print("=======================================================")
    print("      SignTalk Phase 2: TFLite Quantization & Deploy   ")
    print("=======================================================")
    convert_and_deploy_tflite(quant_mode='float16')
