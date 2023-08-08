import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import requests
import json
from pytube import YouTube
import os

def get_playlist_videos(playlist_url):
    playlist_id = playlist_url.split("list=")[1]
    api_key = "AIzaSyA4w27bFloeNXlhfs7K3JIbuhNa7xz1sqk"
    video_urls = []
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={playlist_id}&key={api_key}"
    response = requests.get(url)
    json_data = json.loads(response.text)

    # Append urls in an array
    for item in json_data["items"]:
        video_id = item["snippet"]["resourceId"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_urls.append(video_url)

    # Prob of 50 results/page. If results > 50, we go again.
    while "nextPageToken" in json_data:
        next_page_token = json_data["nextPageToken"]

        # API call here will be made with the next page token.
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={playlist_id}&key={api_key}&pageToken={next_page_token}"
        response = requests.get(url)
        json_data = json.loads(response.text)

        # Extract urls from response and add them to the array.
        for item in json_data["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_urls.append(video_url)

    print(len(video_urls))
    return video_urls

def download_videos(video_urls, quality, output_folder):
    count = 0
    for video_url in video_urls:
        count += 1
        try:
            video = YouTube(video_url)
            stream = video.streams.filter(res=quality, progressive=True).first()
            if stream:
                video_title = f"{count}-{video.title}"
                output_path = os.path.join(output_folder, video_title)
                if os.path.exists(output_path):
                    print(f"Skipping video: {video_title} (already downloaded)")
                else:
                    print(f"Downloading video: {video_title}")
                    stream.download(output_path=output_folder, filename_prefix= str(count) + "-")
                    print(f"Downloaded: {video_title}")
            else:
                print(f"No available stream for video: {video.title}")
        except Exception as e:
            print(f"Error occurred while downloading video: {video_url}")
            print(f"Error: {str(e)}")

    print("All videos downloaded successfully!")


def choose_folder():
    #print(choosing folder)
    global output_folder
    output_folder = filedialog.askdirectory()
    folder_path_label.config(text=output_folder)


def download_playlist():
    playlist_url = playlist_url_entry.get()
    video_urls = get_playlist_videos(playlist_url)
    quality = quality_var.get()  # Get the selected video quality

    download_videos(video_urls, quality, output_folder)


def download_single_video():
    video_url = video_url_entry.get()
    try:
        video = YouTube(video_url)
        quality = quality_var.get()  # Get the selected video quality
        stream = video.streams.filter(res=quality, progressive=True).first()
        if stream:
            video_title = f"Video - ({video.title})"
            output_path = os.path.join(output_folder, f"{video_title}.mp4")
            if os.path.exists(output_path):
                print(f"Skipping video: {video_title} (already downloaded)")
            else:
                print(f"Downloading video: {video_title}")
                stream.download(output_path=output_folder)
                print(f"Downloaded: {video_title}")
        else:
            print(f"No available stream for video: {video.title}")
    except Exception as e:
        print(f"Error occurred while downloading video: {video_url}")
        print(f"Error: {str(e)}")


# Create the main window
window = tk.Tk()
window.title("YouTube Downloader")
window.geometry("330x450")
window.resizable(False, False)

# Create a styled frame for the content
content_frame = ttk.Frame(window, padding=20)
content_frame.grid(row=0, column=0, sticky="nsew")

# Placeholder to enter URL of single video
video_label = ttk.Label(content_frame, text="YouTube Video URL:")
video_label.grid(row=0, column=0, pady=10, sticky="w")

video_url_entry = ttk.Entry(content_frame, width=50)
video_url_entry.grid(row=1, column=0, pady=5)

# Download single video button
download_single_video_button = ttk.Button(content_frame, text="Download Video", command=download_single_video)
download_single_video_button.grid(row=2, column=0, pady=10)

# Separator
ttk.Separator(content_frame, orient="horizontal").grid(row=3, column=0, sticky="we", pady=20)

# Placeholder to enter URL of playlist
playlist_label = ttk.Label(content_frame, text="YouTube Playlist URL:")
playlist_label.grid(row=4, column=0, pady=10, sticky="w")

playlist_url_entry = ttk.Entry(content_frame, width=50)
playlist_url_entry.grid(row=5, column=0, pady=5)

# Selection of the output folder
output_folder_button = ttk.Button(content_frame, text="Choose Output Folder", command=choose_folder)
output_folder_button.grid(row=8, column=0, pady=10)

folder_path_label = ttk.Label(content_frame, text="")
folder_path_label.grid(row=7, column=0)

# Download playlist button
download_playlist_button = ttk.Button(content_frame, text="Download Playlist", command=download_playlist)
download_playlist_button.grid(row=6, column=0, pady=10)

quality_label = ttk.Label(content_frame, text="Video Quality:")
quality_label.grid(row=9, column=0, pady=10, sticky="w")

quality_var = tk.StringVar()
quality_dropdown = ttk.Combobox(content_frame, width=10, textvariable=quality_var)
quality_dropdown['values'] = ['1080p', '720p', '480p', '360p', '240p', '144p']
quality_dropdown.current(0)
quality_dropdown.grid(row=10, column=0, pady=5)

# Run the main GUI
window.mainloop()
