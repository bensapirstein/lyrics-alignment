import yt_dlp
import os
import subprocess  # For running FFmpeg

YOUTUBE_URL_FORMAT = "https://www.youtube.com/watch?v={}"

def download_and_convert_to_mp3(url, output_path, dst_filename=None):
    ydl_opts = {
        'format': 'bestaudio/best',  # Get the best audio
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # Output template (initially WebM or MP4)
    }

    yt_url = YOUTUBE_URL_FORMAT.format(url)  # Construct the full URL

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(yt_url, download=False)  # Get info about file before download
            filename = ydl.prepare_filename(info_dict) # Get the filename
            # Check if mp3 file already exists
            mp3_filename = filename.replace(".webm", ".mp3").replace(".mp4", ".mp3") if dst_filename is None else os.path.join(output_path, dst_filename)
            if os.path.exists(mp3_filename):
                print(f"MP3 file already exists: {mp3_filename}")
                return True  # Success

            ydl.download([yt_url])  # Download the audio (WebM or MP4)
            
            # Run FFmpeg for conversion:
            try:
                subprocess.run(['ffmpeg', '-i', filename, mp3_filename], check=True)  # check=True raises exception on error
                print(f"Conversion to MP3 successful: {mp3_filename}")
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg conversion failed: {e}")
                return False  # Conversion failed

            os.remove(filename)  # Delete the original WebM or MP4 file
            print(f"Deleted original file: {filename}")

            return True  # Success

        except Exception as e:
            print(f"Download or other error: {e}")
            return False