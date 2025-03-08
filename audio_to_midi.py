import csv
import mido
from mido import Message, MidiFile, MidiTrack
import librosa
import os

# Input files
alignment_csv = "predictions_bdr_MTL/נסרין - לא לפנות אליי (Prod. by Jordi)_align.csv"
lyrics_file = "lyrics/נסרין - לא לפנות אליי (Prod. by Jordi).words.txt"
audio_file = "mp3/נסרין - לא לפנות אליי (Prod. by Jordi).mp3"
output_midi = "midi/נסרין - לא לפנות אליי (Prod. by Jordi).mid"

# Make output directory if it doesn’t exist
os.makedirs(os.path.dirname(output_midi), exist_ok=True)

# Load audio to determine duration
y, sr = librosa.load(audio_file, sr=None)
audio_duration = librosa.get_duration(y=y, sr=sr)

# Read lyrics file
with open(lyrics_file, 'r', encoding='utf-8') as f:
    words = [line.strip() for line in f.readlines()]

# Read alignment CSV
aligned_words = []
with open(alignment_csv, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        word, start_time, end_time = words[i], float(row[0]), float(row[1])
        aligned_words.append((word, start_time, end_time))

# Create MIDI file
midi = MidiFile()
track = MidiTrack()
midi.tracks.append(track)


# Adjust tempo dynamically based on song duration
def calculate_tempo(audio_duration, midi_ticks_per_beat, beats_per_minute=120):
    return mido.bpm2tempo((60 / audio_duration) * (midi_ticks_per_beat * 2))


tempo = calculate_tempo(audio_duration, midi.ticks_per_beat)
ticks_per_beat = midi.ticks_per_beat
track.append(mido.MetaMessage('set_tempo', tempo=tempo))


# Convert time to MIDI ticks
def time_to_ticks(time_sec, ticks_per_beat, tempo):
    return int(mido.second2tick(time_sec, ticks_per_beat, tempo))


# Create MIDI notes for each word
previous_tick = 0
base_note = 60  # Middle C (C4)
for word, start_time, end_time in aligned_words:
    start_tick = time_to_ticks(start_time, ticks_per_beat, tempo)
    end_tick = time_to_ticks(end_time, ticks_per_beat, tempo)
    duration = max(1, end_tick - start_tick)
    delta_time = start_tick - previous_tick  # Ensure relative timing

    track.append(Message('note_on', note=base_note, velocity=64, time=delta_time))
    track.append(Message('note_off', note=base_note, velocity=64, time=duration))
    track.append(mido.MetaMessage('lyrics', text=word, time=0))

    previous_tick = start_tick  # Update for next word's delta time

# Save MIDI file
midi.save(output_midi)
print(f"MIDI file saved as {output_midi}")