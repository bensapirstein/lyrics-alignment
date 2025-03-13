import mido
from mido import Message, MidiFile, MidiTrack
import csv
import os
from pydub import AudioSegment
import librosa


def create_alignment_midi(mp3_file, lyrics_file, alignment_csv, output_midi, bpm=120):
    # Get audio duration from MP3
    audio = AudioSegment.from_mp3(mp3_file)
    audio_duration_ms = len(audio)
    audio_duration_sec = audio_duration_ms / 1000.0

    # Load audio to get duration and tempo information
    y, sr = librosa.load(mp3_file, sr=None)
    audio_duration = librosa.get_duration(y=y, sr=sr)
    # Try to estimate tempo
    bpm, _ = librosa.beat.beat_track(y=y, sr=sr)
    # Convert BPM to microseconds per beat
    bpm = int(bpm)


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

    num_words = len(aligned_words)

    # Create MIDI file
    mid = MidiFile(type=1)

    # Add a tempo track
    tempo_track = MidiTrack()
    mid.tracks.append(tempo_track)

    # Set tempo (microseconds per beat)
    tempo = mido.bpm2tempo(bpm)
    tempo_track.append(Message('program_change', program=0, time=0))
    tempo_track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    # Add end of track marker with duration that matches the audio
    # Convert audio duration to MIDI ticks
    ticks_per_beat = mid.ticks_per_beat
    total_ticks = int((audio_duration_sec / 60.0) * bpm * ticks_per_beat)
    tempo_track.append(mido.MetaMessage('end_of_track', time=total_ticks))

    # Create a track for the word alignment
    track = MidiTrack()
    mid.tracks.append(track)

    # Choose a distinct instrument (program) number
    # 74 is recorder/flute, which might be good for speech
    track.append(Message('program_change', program=74, time=0))

    # Add notes for each word
    last_end_time = 0
    for i, (word, start_time, end_time) in enumerate(aligned_words):
        # break after 64 notes
        if i == 64:
            break
        # Calculate note length in MIDI ticks
        start_time_ticks = int((start_time / 60.0) * bpm * ticks_per_beat)
        end_time_ticks = int((end_time / 60.0) * bpm * ticks_per_beat)
        duration_ticks = end_time_ticks - start_time_ticks

        # Calculate delta time from previous note
        delta_ticks = start_time_ticks - last_end_time if last_end_time > 0 else start_time_ticks

        
        # Assign a MIDI note number
        note_number = 60 + (i % 16)

        # Add note on event
        track.append(Message('note_on', note=note_number, velocity=64, time=delta_ticks))

        # Add note off event
        track.append(Message('note_off', note=note_number, velocity=64, time=duration_ticks))

        last_end_time = end_time_ticks

    # Add end of track marker
    remaining_ticks = total_ticks - last_end_time
    track.append(mido.MetaMessage('end_of_track', time=remaining_ticks))

    # Save MIDI file
    mid.save(output_midi)
    print(f"MIDI file saved: {output_midi}")
    print(f"Audio duration: {audio_duration_sec} seconds")
    print(f"MIDI duration in ticks: {total_ticks}")


# Example usage
if __name__ == "__main__":
    base_dir = "data_pipeline/Semitic"
    title = "A-WA - ＂Hana Mash Hu Al Yaman＂ (Official Video)"
    artist = "A-WA"
    model = "bdr_MTL"
    alignment_csv = os.path.join(base_dir, "predictions_{model}/{title}_align.csv".format(title=title, model=model))
    lyrics_file = os.path.join(base_dir, "lyrics/{title}.words.txt".format(title=title))
    mp3_file = os.path.join(base_dir, "mp3/{title}.mp3".format(title=title))
    output_midi = os.path.join(base_dir, "midi/{artist}/{title}_{model}.mid".format(artist=artist, title=title, model=model))

    create_alignment_midi(mp3_file, lyrics_file, alignment_csv, output_midi)