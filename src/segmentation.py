"""Video segmentation using DeepLabv3."""

import torch
import torchvision
from torchvision import transforms
import numpy as np
from typing import List, Optional, Tuple
import cv2
from PIL import Image


class VideoSegmenter:
    """
    Video segmentation using DeepLabv3 ResNet-101 from torchvision.
    """
    
    # COCO class labels (21 classes for DeepLabv3)
    CLASSES = {
        0: 'background',
        15: 'person',
        7: 'car',
        6: 'bus',
        8: 'truck',
        9: 'boat',
        17: 'cat',
        18: 'dog',
        19: 'horse',
        20: 'sheep',
        21: 'cow',
    }
    
    def __init__(self, device: Optional[str] = None):
        """
        Initialize the video segmenter.
        
        Args:
            device: Device to use ('cuda' or 'cpu'). If None, auto-detect.
        """
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        # Load pre-trained DeepLabv3 model
        self.model = torchvision.models.segmentation.deeplabv3_resnet101(
            pretrained=True
        ).to(self.device)
        self.model.eval()
        
        # Define preprocessing transform
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def _preprocess_frame(self, frame: np.ndarray) -> torch.Tensor:
        """
        Preprocess a frame for model input.
        
        Args:
            frame: Frame as numpy array (BGR format from OpenCV)
            
        Returns:
            Preprocessed tensor
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Manual tensor conversion (bypasses torchvision ToTensor for NumPy 2.x compatibility)
        img = frame_rgb.astype('float32') / 255.0
        img = img. transpose((2, 0, 1))  # HWC -> CHW format
        input_tensor = torch.tensor(img, dtype=torch.float32)
        
        # Apply ImageNet normalization manually
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        input_tensor = (input_tensor - mean) / std
        
        return input_tensor
    
    def _postprocess_output(
        self,
        output: torch.Tensor,
        target_size: Tuple[int, int],
        target_class: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Postprocess model output to get masks.
        
        Args:
            output: Model output tensor
            target_size: (height, width) for output mask
            target_class: Specific class to extract. If None, use argmax.
            
        Returns:
            Tuple of (binary_mask, probability_map)
        """
        # Get probability maps
        probs = torch.softmax(output, dim=1)
        
        if target_class is not None:
            # Extract specific class
            prob_map = probs[0, target_class].cpu().numpy()
            binary_mask = (prob_map > 0.5).astype(np.uint8)
        else:
            # Use argmax
            predictions = torch.argmax(probs, dim=1)[0].cpu().numpy()
            # Create binary mask (foreground vs background)
            binary_mask = (predictions > 0).astype(np.uint8)
            # For probability map, use max probability across all classes
            prob_map = torch.max(probs[0], dim=0)[0].cpu().numpy()
        
        # Resize to original size
        binary_mask = cv2.resize(
            np.asarray(binary_mask, dtype=np.float32),
            (target_size[1], target_size[0]),
            interpolation=cv2.INTER_NEAREST
        ).astype(np.uint8)
        
        prob_map = cv2.resize(
            np.asarray(prob_map, dtype=np. float32),
            (target_size[1], target_size[0]),
            interpolation=cv2.INTER_LINEAR
        ).astype(np.float32)
        
        return binary_mask, prob_map
    
    def segment_frame(
        self,
        frame: np.ndarray,
        target_class: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Segment a single frame.
        
        Args:
            frame: Input frame as numpy array (BGR)
            target_class: Target class ID (e.g., 15 for person)
            
        Returns:
            Tuple of (binary_mask, probability_map)
        """
        original_size = frame.shape[:2]  # (height, width)
        
        # Preprocess
        input_tensor = self._preprocess_frame(frame).unsqueeze(0).to(self.device)
        
        # Inference
        with torch.no_grad():
            output = self.model(input_tensor)['out']
        
        # Postprocess
        binary_mask, prob_map = self._postprocess_output(
            output, original_size, target_class
        )
        
        return binary_mask, prob_map
    
    def segment_video(
        self,
        frames: List[np.ndarray],
        target_class: Optional[int] = None,
        batch_size: int = 4
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Segment all frames in a video.
        
        Args:
            frames: List of video frames
            target_class: Target class ID (e.g., 15 for person)
            batch_size: Number of frames to process in parallel
            
        Returns:
            Tuple of (binary_masks, probability_maps)
        """
        binary_masks = []
        probability_maps = []
        
        num_frames = len(frames)
        original_size = frames[0].shape[:2]
        
        # Process in batches
        for i in range(0, num_frames, batch_size):
            batch_frames = frames[i:i + batch_size]
            
            # Preprocess batch
            batch_tensors = torch.stack([
                self._preprocess_frame(frame) for frame in batch_frames
            ]).to(self.device)
            
            # Inference
            with torch.no_grad():
                outputs = self.model(batch_tensors)['out']
            
            # Postprocess each output
            for j, output in enumerate(outputs):
                binary_mask, prob_map = self._postprocess_output(
                    output.unsqueeze(0), original_size, target_class
                )
                binary_masks.append(binary_mask)
                probability_maps.append(prob_map)
        
        return binary_masks, probability_maps
    
    @staticmethod
    def get_class_id(class_name: str) -> Optional[int]:
        """
        Get class ID from class name.
        
        Args:
            class_name: Name of the class (e.g., 'person', 'car')
            
        Returns:
            Class ID or None if not found
        """
        for class_id, name in VideoSegmenter.CLASSES.items():
            if name.lower() == class_name.lower():
                return class_id
        return None
    
    @staticmethod
    def get_available_classes() -> dict:
        """
        Get dictionary of available classes.
        
        Returns:
            Dictionary mapping class IDs to class names
        """
        return VideoSegmenter.CLASSES.copy()
