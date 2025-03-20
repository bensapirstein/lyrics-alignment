# lyrics-alignment
A tool for real-time lyrics alignment and visualization, integrating audio processing, word-level synchronization, and interactive variable font typography.

## Notebooks
- **download_music.ipynb:** Downloads audio from YouTube URLs.
- **separate_voices.ipynb:** Uses Spleeter to separate the vocals from the original songs.
- **prepare_dali.ipynb:** Aimed to download DALI data and separate it, but was computationally expensive.
- **prepare_lyrics.ipynb:** Transliterates and formats lyrics to the input format.
- **evaluate.ipynb:** Evaluates the results, compares predictions to ground truth, computes metrics, and plots graphs.
- **pipeline.ipynb:** Implements a full pipeline to download a song from YouTube, separate the vocals, process the lyrics, and generate a MIDI file.

## Scripts
- **predict_MTL.sh:** Runs experiments on German, Spanish, French, Semitic languages (Arabic and Hebrew), and English for validating versus the original paper.
- **predict_baseline.sh:** Runs baseline experiments.
- **predict_bdr_MTL.sh:** Runs experiments with boundary detection and multi-task learning.
- **predict_bdr_baseline.sh:** Runs baseline experiments with boundary detection.
- **alignment_to_midi.py:** Converts the resulted alignment CSV to a MIDI file, considering the song tempo.

Predictions are stored under the `predictions/` directory, and raw results are aggregated in `all_results.csv`.



## Architecture
The system architecture is modular and comprises the following key components:
1. **Audio Retrieval and Pre-Processing:** Songs are downloaded and processed to separate vocals from accompaniments.
2. **Lyrics Transliteration:** Non-English lyrics are romanized using a large language model.
3. **Acoustic Model with Multi-Task Learning:** A pre-trained acoustic model processes Mel-spectrograms and outputs phoneme and pitch probabilities.
4. **Alignment Algorithm:** Phoneme posteriorgrams are aligned with lyrics using a Viterbi forced-alignment approach.
5. **MIDI file creation:** Onset and offset timestamps for each word are used to create MIDI files and synchronized lyric videos.

## Experiments
The system is evaluated on the Jamendo dataset using the following metrics:
- **Average Absolute Error (AAE):** Measures the mean temporal deviation between predicted and ground-truth word onsets.
- **Percentage of Correct Onsets (PCO):** Indicates the proportion of words for which the predicted onset falls within a specified tolerance window.

## Results
The proposed system achieves good performance on multiple languages, demonstrating the potential for using pre-trained models across different languages. Detailed results are as follows:

| Model          | English AAE (s) | English PCO (%) | German AAE (s) | German PCO (%) | Spanish AAE (s) | Spanish PCO (%) | French AAE (s) | French PCO (%) |
|----------------|-----------------|-----------------|----------------|----------------|-----------------|-----------------|----------------|----------------|
| MTL            | 0.459           | 93.36           | 0.414          | 94.00          | 0.427           | 89.44           | 0.757          | 77.35          |
| Baseline       | 0.438           | 93.08           | 0.590          | 93.35          | 0.367           | 92.19           | 0.469          | 82.73          |
| BDR + MTL      | 0.460           | 93.41           | 0.414          | 94.06          | 0.427           | 89.51           | 0.752          | 77.45          |
| BDR + Baseline | 0.438           | 93.13           | 0.588          | 93.44          | 0.380           | 92.43           | 0.468          | 82.75          |

## Contributing
We welcome contributions! Please follow these steps to contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments
The author thanks the developers of Spleeter, the creators of the DALI dataset, and the research teams behind recent advances in lyrics alignment for providing foundational work that enabled this project.

The code for the project is openly accessible on GitHub: [https://github.com/bensapirstein/lyrics-alignment](https://github.com/bensapirstein/lyrics-alignment)
