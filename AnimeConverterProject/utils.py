import os
import logging

def ensure_output_directory(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")
