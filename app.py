import gradio as gr
import torch
from PIL import Image
import os 
import pathlib

# Fixing path issue for Windows
# temp = pathlib.PosixPath
# pathlib.PosixPath = pathlib.WindowsPath

# Load your custom weights
weights_path = 'yolov5/runs/train/road_damage_detection/weights/best.pt'  # Update this path to your actual weights file
model = torch.hub.load('ultralytics/yolov5', 'custom', weights_path, force_reload=True)
model.names = ["D00", "D10", "D20", "D40"]

def yolo(im, size=640):
    # Resize image while maintaining aspect ratio
    g = (size / max(im.size))  # Gain
    im = im.resize(tuple(int(x * g) for x in im.size))  # Resize
    
    # Perform inference
    results = model(im)
    
    # Render results (updates results.imgs with boxes and labels)
    results.render()
    
    # Save the result image
    output_path = "image0.jpg"
    results.save(save_dir=".", exist_ok=True)  # Save in the current directory
    
    # Prepare Markdown text information
    unique_labels = set()  # To track unique labels
    for i, label in enumerate(results.names):
        # Collect detection information
        boxes = results.xyxy[0].cpu().numpy()
        for box in boxes:
            if int(box[5]) == i:
                label_text = f"{results.names[i]} -> {label_mapping.get(results.names[i], 'Unknown')}"
                unique_labels.add(label_text)  # Add unique label to set
    
    # Join unique labels into Markdown formatted string
    markdown_text = "<br>".join(unique_labels) if unique_labels else "No damage detected."
    
    return output_path, markdown_text

# Label mapping for display
label_mapping = {
    "D00": "Longitudinal Crack",
    "D10": "Transverse Crack",
    "D20": "Alligator Crack",
    "D40": "Pothole"
}

inputs = gr.Image(type="pil", label="Input Image")
outputs = [gr.Image(type="pil", label="Output Image"), gr.Markdown(label="Detection Info")]

title = "Road Damage Detection"
description = "The Road Damage Detection project utilizes the YOLO model to automate the detection and classification of road damage from images. By processing images to identify and categorize damage types such as cracks and potholes, the project aims to enhance infrastructure management through timely and efficient maintenance. The model is trained on annotated datasets and evaluated using Intersection over Union (IoU) to ensure accuracy. This approach reduces the need for manual inspections, improving road safety and maintenance efficiency."

examples = [['India_009852.jpg'], ['Japan_011558.jpg'], ['usa.jpg']]

gr.Interface(fn=yolo, inputs=inputs, outputs=outputs, title=title, description=description, examples=examples).launch()
