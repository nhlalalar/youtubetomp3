from flask import Flask, render_template, request, redirect, url_for
from pytube import YouTube
import os
import re
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    # Get the YouTube video link from the HTML form
    link = request.form["link"]

    # Download the audio from the YouTube video using pytube
    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=True).first()

    # Create the output directory if it does not exist
    output_dir = "static/downloads"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Replace special characters in the video title
    title = re.sub(r'[^\w\s-]', '', yt.title)
    title = re.sub(r'[-\s]+', '-', title)
    output_file = f"{title}.mp4"

    # Download the audio stream to the output directory with the modified title
    stream.download(output_path=output_dir, filename=output_file)

    # Use ffmpeg to convert the downloaded file to MP3 format
    input_file = os.path.join(output_dir, output_file)
    output_file = f"{title}.mp3"
    output_path = os.path.join(output_dir, output_file)
    subprocess.call(['ffmpeg', '-i', input_file, '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k', output_path])

    # Delete the original downloaded file
    os.remove(input_file)

    # Redirect to the page that plays the MP3 file
    return redirect(url_for("play_page", filename=f"{title}.mp3"))

@app.route("/play/<filename>")
def play_page(filename):
    return render_template("play.html", filename=filename)

if __name__ == "__main__":
    app.run(debug=True)
