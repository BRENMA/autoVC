# autoVC

autoVC is an open-source tool that simplifies deal flow management for venture capitalists, startup enthusiasts, or anyone managing investment opportunities. Forward deal blurbs to a Telegram bot, which ingests all relevant data, scrapes associated websites and pitch decks, summarizes the deal using AI, and posts it to a Notion database for easy access and review.

## Features

- **Telegram Integration**: Forward any deal information directly to the bot on Telegram.
- **Automated Data Ingestion**: The bot scrapes websites, pitch decks, and other relevant resources.
- **AI-Powered Summarization**: The bot summarizes the deal using AI for quick insights.
- **Notion Integration**: Deals are posted to a Notion database, making deal flow management seamless and organized.

## Prerequisites

Before you can use autoVC, you need to set up the following:

1. **Telegram Bot**: Create a bot on Telegram to receive deal blurbs.
2. **Notion Integration**: Set up a Notion integration to post summarized deals into a Notion database.
3. **OpenAI API**: Obtain an API key from OpenAI for AI-powered summarization.
4. **Selenium**: Set up the webdriver (Chrome)

## Installation

1. Clone the repository

2. Install dependencies:

  Using Anaconda:
   - Create a new enviroment with Python 3.11.10
   - ```conda install -c conda-forge cudatoolkit=11.2.2 cudnn=8.1.0```
   - ```pip install -r requirements.txt```


4. Set up environment variables. Create a `.env` file in the root directory and include the following variables:

    ```env
    TELEGRAM_BOT_TOKEN=your-telegram-bot-token
    NOTION_API_KEY=your-notion-api-key
    NOTION_DATABASE_ID=your-notion-database-id
    OPENAI_API_KEY=your-openai-api-key
    EMAIL_FOR_DOCSEND=the email you want to use when accessing docsend links
    ```

5. Run the application:

    ```bash
    python telegramBot.py
    ```

## Usage

1. Start forwarding deal blurbs to the telegram bot.
2. The bot will automatically handle the ingestion, summarization, and Notion posting process.
3. Check your Notion database for new deal summaries and details.
