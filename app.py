import os
import logging
from flask import Flask, request, render_template, flash, redirect, url_for, send_from_directory
from pytube import YouTube, Playlist, Channel, exceptions

# --- Configuration ---
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(APP_ROOT, 'downloads')
ALLOWED_EXTENSIONS = {'mp4', 'mp3'} # Basic example, pytube handles streams

# Ensure download folder exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

app = Flask(__name__)
# IMPORTANT: Secret key is needed for flashing messages!
# Generate a strong random key in a real application (e.g., using os.urandom(24))
# For Netlify/other hosting, use environment variables.
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_default_dev_secret_key')
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Functions ---

def sanitize_filename(filename):
    """Removes characters that are problematic in filenames."""
    # Remove invalid chars (you might want a more robust regex)
    sanitized = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
    # Replace spaces with underscores (optional)
    sanitized = sanitized.replace(' ', '_')
    return sanitized

def download_video(url, download_path):
    """Downloads a single YouTube video."""
    try:
        yt = YouTube(url)
        # Filter for progressive streams (video+audio) and get highest resolution
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not stream:
            # Fallback if no progressive mp4 found (less common now)
            stream = yt.streams.get_highest_resolution() # Might be webm or other

        if not stream:
             flash(f"ERROR: No suitable video stream found for {yt.title}", "error")
             return None, None

        logging.info(f"Attempting to download: {yt.title} (Resolution: {stream.resolution})")
        # Sanitize filename before saving
        safe_filename = sanitize_filename(yt.title) + '.' + stream.subtype # Use stream's actual extension
        output_file = stream.download(output_path=download_path, filename=safe_filename)
        logging.info(f"Successfully downloaded: {output_file}")
        # Return the filename for potential linking/display (relative to download folder)
        return safe_filename, yt.title

    except exceptions.RegexMatchError:
        flash("ERROR: Invalid YouTube URL.", "error")
        logging.error(f"RegexMatchError for URL: {url}")
        return None, None
    except exceptions.VideoUnavailable:
        flash(f"ERROR: Video {url} is unavailable (private, deleted, etc.).", "error")
        logging.error(f"VideoUnavailable for URL: {url}")
        return None, None
    except exceptions.PytubeError as e:
        flash(f"ERROR: An error occurred with pytube: {str(e)}", "error")
        logging.error(f"PytubeError for URL {url}: {e}")
        return None, None
    except Exception as e:
        flash(f"ERROR: An unexpected error occurred: {str(e)}", "error")
        logging.exception(f"Unexpected error for URL {url}: {e}") # Log full traceback
        return None, None

# --- Flask Routes ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main page with the input form."""
    return render_template('index.html', title="YouTube Downloader - Download Videos, Playlists, Channels")

@app.route('/download', methods=['POST'])
def handle_download():
    """Handles the download request based on the URL type."""
    url = request.form.get('url', '').strip()
    if not url:
        flash("Please enter a YouTube URL.", "warning")
        return redirect(url_for('index'))

    download_type = "unknown"
    downloaded_files = [] # Store tuples of (filename, title)

    try:
        # 1. Try Playlist
        if 'playlist?list=' in url:
            pl = Playlist(url)
            logging.info(f"Processing Playlist: {pl.title} ({len(pl.video_urls)} videos)")
            flash(f"Processing Playlist: '{pl.title}'. This might take a while...", "info")
            download_type = "Playlist"
            count = 0
            limit = 50 # SAFETY LIMIT - Adjust as needed or make configurable
            for video_url in pl.video_urls:
                if count >= limit:
                    flash(f"WARNING: Playlist download limited to the first {limit} videos.", "warning")
                    logging.warning(f"Playlist '{pl.title}' download stopped at {limit} videos.")
                    break
                filename, title = download_video(video_url, app.config['DOWNLOAD_FOLDER'])
                if filename and title:
                    downloaded_files.append((filename, title))
                    # Optional: Flash progress per video (can be noisy)
                    # flash(f"Downloaded video {count+1}/{len(pl.video_urls)}: {title}", "info")
                else:
                    # Error already flashed by download_video
                    pass
                count += 1
            if downloaded_files:
                 flash(f"Playlist '{pl.title}' processing complete. {len(downloaded_files)} videos downloaded (or attempted).", "success")
            else:
                 flash(f"Could not download any videos from playlist '{pl.title}'. Check logs.", "error")


        # 2. Try Channel (More complex - gets video URLs *currently* listed)
        # Note: Pytube's Channel object might not get *all* videos efficiently for large channels.
        elif '/channel/' in url or '/user/' in url or '/c/' in url:
            # Make sure pytube handles these variants
            # Use a try-except block as Channel initialization can fail
            try:
                 c = Channel(url)
                 logging.info(f"Processing Channel: {c.channel_name} (Fetching video list...)")
                 flash(f"Processing Channel: '{c.channel_name}'. Fetching video list, this can take time...", "info")
                 download_type = "Channel"
                 count = 0
                 limit = 50 # SAFETY LIMIT - Adjust as needed
                 # Be aware channel.video_urls can be slow/incomplete for huge channels
                 video_urls = list(c.video_urls) # Get URLs first to show progress estimate
                 num_videos = len(video_urls)
                 flash(f"Found approximately {num_videos} videos for channel '{c.channel_name}'. Starting download (limit {limit})...", "info")

                 for video_url in video_urls:
                     if count >= limit:
                         flash(f"WARNING: Channel download limited to the first {limit} videos found.", "warning")
                         logging.warning(f"Channel '{c.channel_name}' download stopped at {limit} videos.")
                         break
                     filename, title = download_video(video_url, app.config['DOWNLOAD_FOLDER'])
                     if filename and title:
                         downloaded_files.append((filename, title))
                         # Optional: Flash progress
                         # flash(f"Downloaded video {count+1}/{min(num_videos, limit)}: {title}", "info")
                     else:
                         pass # Error already flashed
                     count += 1

                 if downloaded_files:
                     flash(f"Channel '{c.channel_name}' processing complete. {len(downloaded_files)} videos downloaded (or attempted).", "success")
                 else:
                     flash(f"Could not download any videos from channel '{c.channel_name}'. Check logs.", "error")

            except Exception as e:
                 # Channel URL might be malformed, or it might be a single video URL
                 # Fall through to single video check
                 logging.warning(f"Could not process URL as Channel ('{url}'): {e}. Trying as single video.")
                 flash("Could not process as Channel. Trying as single video.", "info")
                 # Now attempt as single video (below)

        # 3. Try Single Video (Default/Fallback)
        # Add this check *after* playlist/channel or ensure the specific URL patterns above are matched first
        if download_type == "unknown" or not downloaded_files: # Only try if not identified or if channel failed
            logging.info(f"Processing as Single Video: {url}")
            download_type = "Video"
            filename, title = download_video(url, app.config['DOWNLOAD_FOLDER'])
            if filename and title:
                downloaded_files.append((filename, title))
                flash(f"Successfully downloaded video: '{title}'", "success")
            # Error messages are handled within download_video

    except exceptions.RegexMatchError:
        flash("ERROR: Invalid YouTube URL format.", "error")
        logging.error(f"Invalid URL format provided: {url}")
    except Exception as e:
        flash(f"ERROR: A critical error occurred during processing: {str(e)}", "error")
        logging.exception(f"Critical error processing URL {url}: {e}")

    # Redirect back to index, messages will be displayed via flash
    # Optionally pass downloaded filenames if you want to list them (more complex template needed)
    return redirect(url_for('index'))


# Route to serve downloaded files (optional, use with caution in production)
# This is simple for local dev. In production, use Nginx/Apache or cloud storage.
@app.route('/files/<filename>')
def downloaded_file(filename):
    """Serves a downloaded file."""
    try:
        # Basic security: Prevent directory traversal
        safe_path = os.path.abspath(os.path.join(app.config['DOWNLOAD_FOLDER'], filename))
        if not safe_path.startswith(os.path.abspath(app.config['DOWNLOAD_FOLDER'])):
             raise FileNotFoundError("Access denied")

        return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        flash(f"Error: File '{filename}' not found or access denied.", "error")
        logging.error(f"Attempted to access non-existent or restricted file: {filename}")
        return redirect(url_for('index')) # Or return a 404 page
    except Exception as e:
        flash(f"ERROR: Could not serve file '{filename}': {str(e)}", "error")
        logging.exception(f"Error serving file {filename}: {e}")
        return redirect(url_for('index'))


# --- Main Execution ---
if __name__ == '__main__':
    # Use debug=True only for development!
    # Use host='0.0.0.0' to make it accessible on your network
    app.run(host='0.0.0.0', port=5000, debug=False) # Turn Debug OFF for production/hosting