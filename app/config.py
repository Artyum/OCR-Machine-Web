import logging
import os


class Config:
    # Default settings
    language = 'pol'
    image_dpi = 300
    optimize = 2
    max_workers = 3

    DATA_DIR = "/data"
    INPUT_DIR = os.path.join(DATA_DIR, "input")
    OUTPUT_DIR = os.path.join(DATA_DIR, "output")
    MERGE_DIR = os.path.join(DATA_DIR, "merge")
    CONFIG_FILE = "config.txt"

    SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.ppm', '.pgm', '.pbm')

    # Ensure required directories exist
    for d in [INPUT_DIR, OUTPUT_DIR, MERGE_DIR]:
        os.makedirs(d, exist_ok=True)

    # Map between config keys in file and class attributes
    config_map = {
        "language": ("language", str),
        "image_dpi": ("image_dpi", int),
        "optimize": ("optimize", int),
        "max_workers": ("max_workers", int),
    }

    @staticmethod
    def load_config():
        """Load configuration from config.txt"""
        path = os.path.join(Config.DATA_DIR, Config.CONFIG_FILE)
        if not os.path.exists(path):
            logging.warning("No config file found, saving defaults.")
            Config.save_config()
            return

        try:
            with open(path, "r", encoding="utf-8") as file:
                for line in file:
                    name, _, value = line.partition("=")
                    name, value = name.strip(), value.strip()

                    if name in Config.config_map:
                        attr_name, caster = Config.config_map[name]
                        try:
                            setattr(Config, attr_name, caster(value))
                        except ValueError:
                            logging.warning(f"Invalid value for {name}: {value}")
        except Exception as e:
            logging.warning(f"Config could not be loaded ({e})")

    @staticmethod
    def save_config():
        """Save current configuration to config.txt"""
        path = os.path.join(Config.DATA_DIR, Config.CONFIG_FILE)
        try:
            with open(path, "w", encoding="utf-8") as file:
                for key, (attr_name, _) in Config.config_map.items():
                    value = getattr(Config, attr_name)
                    file.write(f"{key}={value}\n")
            logging.info(f"Config saved to {path}")
        except Exception as e:
            logging.error(f"Could not save config: {e}")
