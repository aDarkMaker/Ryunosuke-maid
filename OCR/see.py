import os
import json
import tempfile
from pathlib import Path
from cnocr import CnOcr
import cv2
import numpy as np
from PIL import ImageGrab

class ScreenOCR:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'models')
        self.ocr = CnOcr(
            det_model_name='ch_PP-OCRv4_det_server', 
            det_root=model_path, 
            rec_root=model_path
        )
        
    def capture_screen(self):
        try:
            screenshot = ImageGrab.grab()
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            return screenshot_bgr
        except Exception as e:
            print(f"failed: {str(e)}")
            return None
    
    def extract_text_with_position(self, ocr_result):
        texts = []
        for item in ocr_result:
            text_info = {
                'text': item['text'],
                'position': item['position'],  
                'confidence': float(item['score'])  
            }
            texts.append(text_info)
        return texts
        
    def analyze_screen(self):
        try:
            screenshot = self.capture_screen()
            
            if screenshot is None:
                return {
                    'success': False,
                    'error': 'img failed'
                }
                
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_path = tmp_file.name
                cv2.imwrite(temp_path, screenshot)
            
            ocr_out = self.ocr.ocr(temp_path)
            
            os.unlink(temp_path)
            
            texts_with_info = self.extract_text_with_position(ocr_out)

            full_text = '\n'.join([item['text'] for item in texts_with_info])
            
            result = {
                'success': True,
                'data': {
                    'full_text': full_text,
                    'text_blocks': [{'text': item['text'], 'confidence': item['confidence']} for item in texts_with_info],
                    'total_blocks': len(texts_with_info),
                    'avg_confidence': sum(item['confidence'] for item in texts_with_info) / len(texts_with_info) if texts_with_info else 0
                }
            }

            return result
            
        except Exception as e:
            error_msg = f"OCR failed: {str(e)}"
            print(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        

ocr_processor = ScreenOCR()

def see():
    return ocr_processor.analyze_screen()