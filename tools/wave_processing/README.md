# wave_processing_utils

## Installation

To install the required dependencies, run the following command:

```pip install transformers torch torchaudio librosa pandas numpy tqdm```


## Prerequisites

Ensure you have a `labels.csv` file in the folder. The file should include a header with the following format:
```filename,label```

**Note:** Files with spaces in their names will be automatically renamed with underscores using the `rename_wav_files` script.

## Scripts Overview

1. **mp3towave.py**  
   Converts MP3 files to WAV format.

2. **rename_wave_files.py**  
   Renames WAV files by replacing spaces with underscores.

3. **Move files to the "files" folder**  (optional if you are working on a subset of data)
   Organize your files by moving them into the `files` folder.

4. **classify_music.py**  
   Classifies music files based on the provided labels.

5. Upload to dataset as applicable
