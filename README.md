# Agentic AI Email Replier

This project automatically reads emails from your Gmail account, generates AI-powered replies using OpenAI, and saves them as drafts.

## Setup

1. **Google Cloud Setup:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing one.
   - Enable the Gmail API.
   - Create credentials (OAuth 2.0 Client ID) and download `credentials.json` to the project root.

2. **Environment Variables:**
   - Copy `.env` and set your OpenAI API key: `OPENAI_API_KEY=your_key_here`

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Script:**
   ```bash
   python src/main.py
   ```
   - On first run, authenticate with Google in the browser.

The script will process the latest 10 emails, generate replies, and save them as drafts in your Gmail.