from setuptools import setup, find_packages

setup(
    name="ACE-STEP DATA-TOOL",
    version="0.1.0",
    author="Sven kettmann",
    description="Modulares Data-Tool. Erstellt automatisch die Trainingsdaten für ACE-STEP",
    packages=find_packages(),  # Automatically find packages in the current directory
    install_requires=[
        "gradio>=5.35.0",
        "requests",
        "beautifulsoup4",
        "numpy",
        "librosa",
        "mutagen",
        "nltk",
        "soundfile",
        "scipy",
        "matplotlib",
        "resampy",
        "lazy_loader",
        "tinytag",
    ],
    entry_points={
        "console_scripts": [
            "ace-data=webui.app:main",
        ],
    },
    python_requires=">=3.7",
)
