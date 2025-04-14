import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
    QLabel, QFileDialog, QWidget, QSplitter, QGridLayout, QFrame
)
from PyQt6.QtGui import QPixmap, QFont, QPalette, QColor
from PyQt6.QtCore import Qt
from gradio_client import Client, handle_file


class RoadDamageDetector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("桥梁损坏检测系统")
        self.setGeometry(100, 100, 1200, 700)  # 减小高度从800到700
        
        self.uploaded_image_path = None
        self.client = Client("shrey-14/Road-damage-detection")
        
        self.init_ui()
    
    def init_ui(self):
        # Set the application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #212529;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 14px;  /* 减小按钮内边距 */
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QFrame {
                border-radius: 8px;
                background-color: white;
            }
        """)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)  # 减小外边距
        main_layout.setSpacing(8)  # 减小间距
        
        # Header frame
        header_frame = QFrame()
        header_frame.setStyleSheet("padding: 10px; background-color: #e9ecef;")  # 减小内边距
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)  # 减小内边距
        header_layout.setSpacing(3)  # 大幅减小元素间距
        
        # Application title
        title_label = QLabel("道路损坏检测系统")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Application description with author info - 保持原始描述
        description_text = "道路损坏检测项目利用YOLO模型实现对图像中道路损坏的自动化检测与分类。通过处理图像识别裂缝、坑洞等损坏类型，该项目旨在通过及时高效的维护提升基础设施管理水平。模型基于标注数据集进行训练，采用交并比（IoU）指标进行精度评估，有效减少人工巡检需求，提升道路安全性与养护效率。"
        
        # Create a QLabel for the description and author info
        desc_with_author = QLabel(description_text)
        desc_with_author.setWordWrap(True)
        desc_with_author.setStyleSheet("color: #495057; line-height: 1.2;")  # 减小行间距
        header_layout.addWidget(desc_with_author)
        
        # Add author info with bold styling
        author_label = QLabel("<b>作者:</b> 雷达 | <b>Email:</b> dalei@cuhk.edu.hk")
        author_label.setStyleSheet("color: #212529; font-size: 12px; margin-top: 2px;")  # 减小上边距
        author_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(author_label)
        
        # Damage types grid
        damage_types_layout = QGridLayout()
        damage_types_layout.setSpacing(8)  # 减小间距
        damage_types_layout.setContentsMargins(0, 2, 0, 2)  # 减小边距
        
        # Title for damage types
        damage_types_title = QLabel("检测损坏类型:")
        damage_types_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        damage_types_title.setContentsMargins(0, 2, 0, 2)  # 减小边距
        header_layout.addWidget(damage_types_title)
        
        # Damage type descriptions
        damage_types = [
            ("D00", "纵向裂缝", "#fd7e14"),
            ("D10", "横向裂缝", "#20c997"),
            ("D20", "网状裂缝", "#ffc107"),
            ("D40", "坑洞", "#dc3545")
        ]
        
        for i, (code, desc, color) in enumerate(damage_types):
            damage_label = QLabel(f"{code}: {desc}")
            damage_label.setStyleSheet(f"background-color: {color}; color: white; padding: 3px 6px; border-radius: 4px;")
            damage_types_layout.addWidget(damage_label, 0, i)
        
        header_layout.addLayout(damage_types_layout)
        main_layout.addWidget(header_frame)
        
        # Buttons layout
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(15, 5, 15, 5)  # 减小内边距
        button_layout.setSpacing(15)
        
        self.upload_btn = QPushButton("上传图片")
        self.upload_btn.setMinimumHeight(35)  # 减小按钮高度
        self.upload_btn.setFont(QFont("Arial", 11))
        self.upload_btn.clicked.connect(self.upload_image)
        button_layout.addWidget(self.upload_btn)
        
        self.detect_btn = QPushButton("开始检测")
        self.detect_btn.setMinimumHeight(35)  # 减小按钮高度
        self.detect_btn.setFont(QFont("Arial", 11))
        self.detect_btn.clicked.connect(self.start_detection)
        self.detect_btn.setEnabled(False)  # Disable until image is uploaded
        button_layout.addWidget(self.detect_btn)
        
        main_layout.addWidget(button_frame)
        
        # Image display area with splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #dee2e6; }")
        
        # Original image area
        original_container = QFrame()
        original_container.setStyleSheet("background-color: white; padding: 8px;")  # 减小内边距
        original_layout = QVBoxLayout(original_container)
        original_layout.setContentsMargins(8, 5, 8, 5)  # 减小内边距
        original_layout.setSpacing(3)  # 减小间距
        
        original_title = QLabel("原始图片")
        original_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        original_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        original_layout.addWidget(original_title)
        
        self.original_image_label = QLabel()
        self.original_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_image_label.setMinimumSize(450, 350)  # 减小最小尺寸
        self.original_image_label.setStyleSheet("border: 2px dashed #dee2e6; border-radius: 4px; margin: 5px;")  # 减小边距
        original_layout.addWidget(self.original_image_label)
        self.splitter.addWidget(original_container)
        
        # Result image area
        result_container = QFrame()
        result_container.setStyleSheet("background-color: white; padding: 8px;")  # 减小内边距
        result_layout = QVBoxLayout(result_container)
        result_layout.setContentsMargins(8, 5, 8, 5)  # 减小内边距
        result_layout.setSpacing(3)  # 减小间距
        
        result_title = QLabel("检测结果")
        result_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        result_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(result_title)
        
        self.result_image_label = QLabel()
        self.result_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_image_label.setMinimumSize(450, 350)  # 减小最小尺寸
        self.result_image_label.setStyleSheet("border: 2px dashed #dee2e6; border-radius: 4px; margin: 5px;")  # 减小边距
        result_layout.addWidget(self.result_image_label)
        
        self.damage_text = QLabel()
        self.damage_text.setWordWrap(True)
        self.damage_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.damage_text.setStyleSheet("padding: 6px; background-color: #343a40; color: white; border-radius: 4px;")  # 减小内边距
        self.damage_text.setMinimumHeight(50)  # 减小最小高度
        result_layout.addWidget(self.damage_text)
        self.splitter.addWidget(result_container)
        
        main_layout.addWidget(self.splitter, 1)  # Give it a stretch factor of 1
        
        self.setCentralWidget(main_widget)
    
    def upload_image(self):
        file_dialog = QFileDialog()
        file_dialog.setStyleSheet("QFileDialog { background-color: #f8f9fa; }")
        image_path, _ = file_dialog.getOpenFileName(
            self, "选择图片", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if image_path:
            self.uploaded_image_path = image_path
            # Display original image
            self.original_image_label.setStyleSheet("border: none; border-radius: 4px; margin: 5px;")  # 减小边距
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    self.original_image_label.width(), 
                    self.original_image_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio
                )
                self.original_image_label.setPixmap(pixmap)
                self.detect_btn.setEnabled(True)
                
                # Clear previous results
                self.result_image_label.clear()
                self.damage_text.clear()
            else:
                self.original_image_label.setText("无法加载图片")
    
    def start_detection(self):
        if not self.uploaded_image_path:
            return
        
        # Clear previous results
        self.result_image_label.clear()
        self.result_image_label.setStyleSheet("border: none; border-radius: 4px; margin: 5px;")  # 减小边距
        self.damage_text.clear()
        self.damage_text.setText("检测中，请稍候...")
        QApplication.processEvents()  # Update the UI
        
        try:
            # Call the Gradio API
            result = self.client.predict(
                im=handle_file(self.uploaded_image_path),
                api_name="/predict"
            )
            
            # Display result image
            result_image_path = result[0]
            if os.path.exists(result_image_path):
                pixmap = QPixmap(result_image_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        self.result_image_label.width(), 
                        self.result_image_label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio
                    )
                    self.result_image_label.setPixmap(pixmap)
                else:
                    self.result_image_label.setText("无法加载结果图片")
            
            # Display damage text
            if len(result) > 1:
                damage_text = result[1]
                # Translate damage text
                translated_damage = []
                for damage in damage_text.split("<br>"):
                    translated_damage.append(self.translate_damage_type(damage))
                
                self.damage_text.setText("<br>".join(translated_damage))
                self.damage_text.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        
        except Exception as e:
            self.damage_text.setText(f"检测错误: {str(e)}")
    
    def translate_damage_type(self, damage_type):
        damage_mapping = {
            "D00": "纵向裂缝",  # Longitudinal Crack
            "D10": "横向裂缝",  # Transverse Crack
            "D20": "网状裂缝",  # Alligator Crack
            "D40": "坑洞"       # Pothole
        }
        
        if " -> " in damage_type:
            damage_code, damage_desc = damage_type.split(" -> ", 1)
            if damage_code in damage_mapping:
                return f"{damage_code} -> {damage_mapping[damage_code]}"
        
        return damage_type  # Return original if no translation found


def main():
    app = QApplication(sys.argv)
    window = RoadDamageDetector()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()