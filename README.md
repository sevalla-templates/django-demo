# YouTube Downloader (ytdownloader) by MagnatesEmpire.com

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Optional License Badge -->

**Live Demo (if hosted):** [yt.magnatesempire.com](https://yt.magnatesempire.com) <!-- Replace with your actual URL -->
**Author:** [MagnatesEmpire.com](https://magnatesempire.com)

Download YouTube videos, entire playlists, or videos from channels quickly and easily with this web-based tool. Simply paste the URL and hit download!

## ✨ Features

*   **Simple Interface:** Clean, user-friendly web UI.
*   **Video Downloads:** Download individual YouTube videos in the highest available progressive MP4 format.
*   **Playlist Downloads:** Download multiple videos from a YouTube playlist URL. (Includes safety limit)
*   **Channel Downloads:** Download recent videos listed on a YouTube channel page. (Includes safety limit)
*   **Reliable:** Uses the robust `pytube` library for interacting with YouTube.
*   **Web Based:** Access the downloader from any browser.
*   **SEO Friendly:** Basic meta tags included for better search engine visibility.
*   **Open Source:** Feel free to inspect, modify, and contribute.

## 🚀 Technologies Used

*   **Backend:** Python 3
*   **Framework:** Flask
*   **YouTube Interaction:** Pytube
*   **Frontend:** HTML, CSS (Basic)
*   **Deployment (Suggestion):** Gunicorn (for WSGI), Hosting Platform (see below)

## 🛠️ Setup & Installation (Local Development)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/magnatesempire/ytdownloader.git
    cd ytdownloader
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Flask Secret Key (Optional but Recommended for Dev):**
    You can set an environment variable (especially for production) or modify the default in `app.py` for local testing.
    ```bash
    # Linux/macOS
    export FLASK_SECRET_KEY='your_very_strong_random_secret_key'

    # Windows (Command Prompt)
    set FLASK_SECRET_KEY=your_very_strong_random_secret_key

    # Windows (PowerShell)
    $env:FLASK_SECRET_KEY = 'your_very_strong_random_secret_key'
    ```
    *Note: The default key in `app.py` is insecure and only for basic testing.*

5.  **Run the Flask development server:**
    ```bash
    flask run
    # Or: python app.py
    ```

6.  **Access the application:** Open your web browser and go to `http://127.0.0.1:5000` (or the address provided by Flask).

## ⚙️ Usage

1.  Navigate to the web application URL.
2.  Find the YouTube video, playlist, or channel you want to download.
3.  Copy the URL from your browser's address bar.
4.  Paste the URL into the input field on the downloader page.
5.  Click the "Download" button.
6.  The application will identify the URL type (video, playlist, channel) and start the download process.
    *   **Videos:** Will be downloaded to the `downloads` folder on the server. Status messages will appear.
    *   **Playlists/Channels:** The app will iterate through the videos (up to the safety limit defined in `app.py`) and download them. This can take a significant amount of time depending on the size and number of videos.
7.  Check the `downloads` folder in your project directory for the downloaded MP4 files. *(Note: Direct browser download links are not implemented in this basic version but could be added)*.

## ☁️ Deployment

This is a standard Flask application.

**Netlify:**

*   **Challenge:** Netlify primarily hosts **static sites** or sites using **serverless functions**. Directly running a persistent Python/Flask backend like this is **not** Netlify's standard use case.
*   **Possible Workarounds (More Advanced):**
    1.  **Netlify Functions:** Rewrite the core download logic (`handle_download`, `download_video`) into a Netlify Function (written in Node.js, Go, or Python via specific handlers). The frontend HTML/CSS/JS would be static, calling this function via JavaScript (`fetch`). This requires significant changes to the architecture. State management (like download progress) becomes tricky. Long-running downloads might exceed function execution limits.
    2.  **Separate Backend:** Host the Flask application on a platform suitable for Python backends (like Heroku, Render, Google Cloud Run, AWS EC2/Fargate, DigitalOcean App Platform, PythonAnywhere) and have your `yt.magnatesempire.com` domain point to that service. You *could* potentially host just the static `index.html` on Netlify and have its form POST to your externally hosted Flask backend (requires CORS configuration on the Flask app).
*   **Recommendation:** For this type of persistent backend process (especially potentially long-running downloads), platforms like **Render**, **Heroku**, or a **VPS** are generally a better fit than Netlify's primary model.

**Other Platforms (Heroku, Render, VPS, etc.):**

1.  **`Procfile`:** Create a file named `Procfile` (no extension) in the root directory:
    ```
    web: gunicorn app:app
    ```
2.  **Dependencies:** Ensure `gunicorn` is in `requirements.txt`.
3.  **Configuration:** Set the `FLASK_SECRET_KEY` environment variable on your hosting platform. Configure any other necessary environment variables (like database URLs if you add features later).
4.  **Follow Platform Docs:** Consult the documentation for your chosen hosting provider (Render, Heroku, DigitalOcean App Platform, PythonAnywhere, etc.) for specific deployment steps. They usually involve linking your GitHub repo and configuring build/start commands.
5.  **Storage:** Be mindful of disk space on the hosting service. Downloading many large videos can consume significant storage. Consider ephemeral storage limitations on some platforms (downloads might disappear after restarts/redeploys). For persistent storage, look into integrating cloud storage services (like AWS S3, Google Cloud Storage).

## ⚖️ Disclaimer

This tool is provided for educational purposes and personal use only. Please respect YouTube's Terms of Service and copyright laws. **Do not download copyrighted material without explicit permission from the copyright holder.** The developers assume no responsibility for misuse of this tool.

## 🔑 SEO Keywords

YouTube downloader, download YouTube video, YouTube playlist downloader, YouTube channel downloader, free YouTube downloader, online YouTube downloader, video downloader, save YouTube video, python YouTube downloader, Flask YouTube downloader, pytube downloader, magnatesempire, yt.magnatesempire.com, free tool.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues on the [GitHub repository](https://github.com/magnatesempire/ytdownloader).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (You would need to add a LICENSE file, e.g., containing the MIT license text).