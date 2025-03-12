import os
import tqdm
import string 
from src.az_openai import create_client, generate_response

languages = ['Arabic Hebrew', 'French', 'German', 'Spanish']
instructions = {}

for lang in languages:
    with open(f'src/transliteration_guidelines/{lang}.txt', 'r') as f:
        instructions[lang] = f.read()

def filter_content(content):
    # Convert content to lowercase and filter only ASCII lowercase letters, apostrophes, or spaces, keeping newlines
    filtered_content = ''.join([char if char in string.ascii_lowercase + " '\n" else '' for char in content.lower()])
    # Remove apostrophes at the beginning of words or after newlines
    filtered_content = '\n'.join([' '.join([word[1:] if word.startswith("'") else word for word in line.split()]) for line in filtered_content.split('\n')])
    return filtered_content

def save_lyrics_files(dst_folder, filename, filtered_content):
    # Create the .txt filename
    file_path = os.path.join(dst_folder, filename)
    with open(file_path, 'w') as output_file:
        output_file.write(filtered_content)
    
    # Split the filtered content by spaces and newlines, then join with newlines
    words = filtered_content.split()
    words_content = '\n'.join(words)
    
    # Create the .words.txt filename
    words_file_path = os.path.join(dst_folder, filename.replace('.txt', '.words.txt'))
    
    # Write the processed content to the new file
    with open(words_file_path, 'w') as words_file:
        words_file.write(words_content)

def verify_lyrics_file(src_filename, dst_filename):
    with open(src_filename, 'r') as src_file:
        src_content = src_file.read()
        src_words = src_content.split()

    with open(dst_filename.replace('.txt', '.words.txt'), 'r') as dst_file:
        dst_content = dst_file.read()
        dst_words = dst_content.split()

    return len(src_words) == len(dst_words)
    
            
def process_lyrics(data_folder, lang):
    instructions_for_lang = instructions.get(lang)
    if instructions_for_lang is None:
        raise ValueError(f'Language {lang} not supported. Please provide instructions for the language.')
    
    client = create_client()
    lyrics_src_folder = os.path.join(data_folder, 'lyrics_src')
    dst_lyrics_folder = os.path.join(data_folder, 'lyrics')
    lyrics_rom_folder = os.path.join(data_folder, 'lyrics_rom')

    # Create the destination folders if they do not exist
    if not os.path.exists(dst_lyrics_folder):
        os.makedirs(dst_lyrics_folder)
    if not os.path.exists(lyrics_rom_folder):
        os.makedirs(lyrics_rom_folder)

    failed_lyrics = []

    for filename in tqdm.tqdm(os.listdir(lyrics_src_folder)):
        if filename.endswith(".txt"):
            file_path = os.path.join(lyrics_src_folder, filename)
            rom_file_path = os.path.join(lyrics_rom_folder, filename)
            dst_filename = os.path.join(dst_lyrics_folder, filename)
            if os.path.exists(dst_filename):
                print(f"Lyrics file {filename} already processed. Skipping.")
                continue
            
            with open(file_path, "r") as f:
                lyrics = f.read()

            # if romanized lyrics doesn't exist
            if not os.path.exists(rom_file_path):
                # Generate romanized lyrics
                try:
                    romanized_lyrics = generate_response(client, lyrics, instructions_for_lang)
                except Exception as e:
                    print(f"Error processing lyrics file {filename}: {e}")
                    failed_lyrics.append(filename)
                    continue

                if not romanized_lyrics:
                    print(f"Lyrics file {filename} processing failed. No response from the API.")
                    failed_lyrics.append(filename)
                    continue

                with open(rom_file_path, "w") as f:
                    f.write(romanized_lyrics)
            else:
                with open(rom_file_path, "r") as f:
                    romanized_lyrics = f.read()

            # Filter and save structured lyrics
            filtered_content = filter_content(romanized_lyrics)
            save_lyrics_files(dst_lyrics_folder, filename, filtered_content)
            if not verify_lyrics_file(file_path, os.path.join(dst_lyrics_folder, filename)):
                print(f"Lyrics file {filename} processing failed.")
                failed_lyrics.append(filename)
                # remove the failed files
                os.remove(dst_filename)
                os.remove(dst_filename.replace('.txt', '.words.txt'))
                os.remove(rom_file_path)

    print("Lyrics processing complete.")
    if failed_lyrics:
        print("The following lyrics files failed to process:")
        print({lang : failed_lyrics})
    else:
        print("All lyrics files processed successfully.")
