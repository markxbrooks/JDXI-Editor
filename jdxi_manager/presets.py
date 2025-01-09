import json
import os
import logging
from pathlib import Path

class PresetManager:
    """Manages saving and loading of JD-Xi presets"""
    
    def __init__(self):
        # Create presets directory if it doesn't exist
        self.presets_dir = Path.home() / '.jdxi_manager' / 'presets'
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        
        # Preset categories
        self.categories = {
            'analog': self.presets_dir / 'analog',
            'digital1': self.presets_dir / 'digital1',
            'digital2': self.presets_dir / 'digital2',
            'drums': self.presets_dir / 'drums',
            'effects': self.presets_dir / 'effects'
        }
        
        # Create category directories
        for dir_path in self.categories.values():
            dir_path.mkdir(exist_ok=True)
    
    def save_preset(self, category, name, parameters):
        """Save a preset to file"""
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")
            
        file_path = self.categories[category] / f"{name}.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(parameters, f, indent=2)
            logging.info(f"Saved preset: {name} in {category}")
            return True
        except Exception as e:
            logging.error(f"Error saving preset {name}: {e}")
            return False
    
    def load_preset(self, category, name):
        """Load a preset from file"""
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")
            
        file_path = self.categories[category] / f"{name}.json"
        
        try:
            with open(file_path, 'r') as f:
                parameters = json.load(f)
            logging.info(f"Loaded preset: {name} from {category}")
            return parameters
        except Exception as e:
            logging.error(f"Error loading preset {name}: {e}")
            return None
    
    def get_presets(self, category):
        """Get list of available presets for a category"""
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")
            
        preset_dir = self.categories[category]
        presets = [f.stem for f in preset_dir.glob('*.json')]
        return sorted(presets) 