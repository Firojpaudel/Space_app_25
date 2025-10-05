#!/usr/bin/env python3
"""
Script to install required spaCy and scispacy models for the K-OSMOS application.
"""
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a shell command and return success status."""
    try:
        logger.info(f"Running: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"Success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {command}")
        logger.error(f"Error output: {e.stderr}")
        return False

def install_spacy_models():
    """Install required spaCy models."""
    models = [
        "en_core_web_sm",
        "en_core_web_md", 
        "en_core_web_lg"
    ]
    
    logger.info("Installing spaCy models...")
    for model in models:
        success = run_command(f"python -m spacy download {model}")
        if success:
            logger.info(f"✅ Successfully installed {model}")
        else:
            logger.warning(f"⚠️  Failed to install {model}")

def install_scispacy_models():
    """Install scispacy models."""
    models = [
        "en_core_sci_sm",
        "en_core_sci_md",
        "en_core_sci_lg"
    ]
    
    logger.info("Installing scispacy models...")
    for model in models:
        success = run_command(f"pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/{model}-0.5.3.tar.gz")
        if success:
            logger.info(f"✅ Successfully installed {model}")
        else:
            logger.warning(f"⚠️  Failed to install {model}")

def main():
    """Main function to install all models."""
    logger.info("🚀 Starting model installation for K-OSMOS...")
    
    # Install spaCy models
    install_spacy_models()
    
    # Install scispacy models
    install_scispacy_models()
    
    logger.info("🎉 Model installation complete!")
    logger.info("Note: Some models may have failed to install, but the application")
    logger.info("will fall back to pattern-based extraction if needed.")

if __name__ == "__main__":
    main()
