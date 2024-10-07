import logging
import shutil
import json
import csv
import os
import re

from dotenv import load_dotenv

from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import __version__ as TG_VER, ForceReply, Update

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_openai.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.vectorstores import Chroma
from langchain import hub

from notion_client import Client

from webscraping import *
from docusend import *
from webfetch import *
from ingest import *
from ocr import *

load_dotenv()

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

chat = ChatOpenAI(temperature=0, openai_api_key = os.environ.get("OPENAI_API_KEY"))
notion = Client(auth=os.environ.get("NOTION_TOKEN"))

async def process_deal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    inputedText = update.message.text
    
    try:
        #get JSON data from initial message
        master_response = chat.predict("Analyze the following message in [] and return the the startup name, a link to the pitch deck if applicable, the stage of the company if applicable, and a summary of the message. Your response should be in JSON format with four parameters, 'startup', and 'link', 'stage' and 'summary'. For any element that isn't applicable, write N/A. " + '[' + inputedText + ']')
        response = json.loads(master_response)

        company_name = response["startup"]
        r = re.compile('[^a-zA-Z]')
        company_name = r.sub('', company_name)
        print(f"Company name: {company_name}")

        links = re.findall('(?P<url>https?://[^\s]+)', inputedText)
        print(f"Links found: {links}")
        
        #process each link: handle docsend links or call a scraping function for other links
        for link in links:
            if 'docsend' in link:
                getDeckImg(link) #scrape deck and save images to SCREEN_SHOTS
            elif "x.com" not in link:
                loop(link) #extract all relevant URLs and save them to urls.csv
        
        urls = []
        with open("urls.csv", newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                for item in row:
                    urls.append(item)

        #take any links from urls.csv, scrape them, and dump data into SOURCE_DOCUMENTS
        if (len(urls) > 0):
            pageScraper()

        #clean up urls.csv file
        urls_file = open("urls.csv", "w")
        urls_file.truncate()
        urls_file.close()

        documents = []
        #load any documents from SOURCE_DOCUMENTS
        if (len(os.listdir('./SOURCE_DOCUMENTS')) > 0):
            document_pre = load_documents('./SOURCE_DOCUMENTS')
            for doc in document_pre:
                documents.append(doc)

        #clean up SOURCE_DOCUMENTS folder
        for filename in os.listdir("./SOURCE_DOCUMENTS"):
            os.remove("./SOURCE_DOCUMENTS/" + filename)

        #process any deck images with OCR
        deck_text = ""
        if (len(os.listdir('./SCREEN_SHOTS')) > 0):
            deck_text = deck_text + ocrDeck()
            print('Finished collecting deck text')
            #clean up screenshots after processing
            for filename in os.listdir("./SCREEN_SHOTS"):
                os.remove("./SCREEN_SHOTS/" + filename)

        #combine user input and OCR-extracted text into a single text document
        master_text = inputedText + "\n" + deck_text
        with open("./temp_output.txt", "w") as text_file:
            text_file.write(master_text)

        #load the combined text into Langchain as a document
        text_loader = TextLoader('./temp_output.txt')
        text_documents = text_loader.load()
        for doc in text_documents:
            documents.append(doc)
        os.remove("./temp_output.txt")
        print('finished collecting documents')

        #split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        print(f"Loaded {len(documents)} documents")
        print(f"Split into {len(texts)} chunks of text")

        embeddings = OpenAIEmbeddings(openai_api_key = os.environ.get("OPENAI_API_KEY"))

        #create a new directory for the company to store embeddings
        try: 
            os.mkdir(f"./VECTOR_STORES/{company_name}") 
        except OSError as error: 
            print(error) 
        
        #persist the embeddings into a ChromaDB database
        db = Chroma.from_documents(documents=texts, embedding=embeddings, persist_directory = f"./VECTOR_STORES/{company_name}")
        db.persist()
        
        #define questions for analysis and set up the retriever
        questions = [
            f"Explain in detail the problem that {company_name} solves and why no one else has solved it adequately yet.", 
            f"Who are {company_name}'s competitors and why is {company_name} better than them?", 
            f"Provide a thorough background of {company_name}'s founders.", 
        ]
        retriever = db.as_retriever(search_type="mmr", search_kwargs={"k": 5})

        #load a prompt from Langchain Hub and set up question-answering pipeline
        prompt = hub.pull("rlm/rag-prompt")
        qa = (
            {
                "context": retriever,
                "question": RunnablePassthrough(),
            }
            | prompt
            | chat
            | StrOutputParser()
        )

        #run the pipeline to get answer questions
        answers = []
        for question in questions:
            answer = qa.invoke(question)

            print("\n> Question:")
            print(question)
            print("\n> Answer:")
            print(answer)

            answers.append(answer)
            
        #upload deal to Notion
        try:
            text_details = ""
            for text in answers:
                text_details = text_details + str(text) + "\n"

            database_id = os.environ.get("NOTION_DATABASE")

            new_page = {
                'Company': {"title": [{"text": {"content": company_name }}]},
                'Status': {"type": "select", "select": {"name": "0 - Inbound"}},
                'TLDR': {"type": "rich_text", "rich_text": [{"type": "text", "text": {"content": response["summary"] }}]},
                'Round': {"type": "select", "select": {"name": response["stage"]}},
                'Deck': {"type": "url", "url": response["link"]}
            }

            children = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": text_details}
                            }
                        ]
                    }
                }
            ]

            notion.pages.create(
                parent = {"database_id": database_id},
                properties = new_page,
                children=children
            )
            print('added deal to notion')

            await update.message.reply_text("success ✅")

        except Exception as e:
            print(e)

            await update.message.reply_text("try again ❌")

    except Exception as e:
        print(e)
        urls_file = open("urls.csv", "w")
        urls_file.truncate()
        urls_file.close()

        for filename in os.listdir("./SOURCE_DOCUMENTS"):
            os.remove("./SOURCE_DOCUMENTS/" + filename)

        for filename in os.listdir("./SCREEN_SHOTS"):
            os.remove("./SCREEN_SHOTS/" + filename)

        await update.message.reply_text("try again ❌")

def main() -> None:
    application = Application.builder().token(os.environ.get("TELEGRAM_API")).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_deal))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
