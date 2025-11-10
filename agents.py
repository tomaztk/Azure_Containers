import datetime
import os
import sys
import time
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import BingGroundingTool, ConnectedAgentTool, FilePurpose, FileSearchTool, ListSortOrder, MessageRole
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    FileSearchTool,
    FilePurpose,
    ListSortOrder, MessageAttachment
)

load_dotenv("azure.env")
endpoint = os.getenv("PROJECT_ENDPOINT")
credential = DefaultAzureCredential()
project_client = AgentsClient(endpoint=endpoint, credential=credential)

summarization_agent = project_client.create_agent(
    model="gpt-4.1",
    name="putsimply-summarizer-agent",
    instructions="You are a helpful agent to summarize text provide by user or orchestrator agent.",
    temperature=0.7
)

translator_agent = project_client.create_agent(
    model="gpt-4.1",
    name="putsimply-translator-agent",
    instructions="You always translate the input from Slovenian to English.",
    temperature=0.7
)

 
connected_agent_summarify = ConnectedAgentTool(
    id=summarization_agent.id,
    name="summaryagentconnection",
    description="generate a summary of the provided text")

connected_agent_translate = ConnectedAgentTool(
    id=translator_agent.id,
    name="translateagentconnection",
    description="translate the provided text from Slovenian to English"
)

 
orchestrator_agent = project_client.create_agent(
    model="gpt-4.1",
    name="putsimply-orchestrator-agent",
    instructions="You are an orchestrator agent. You take a document from user then you " \
    "need to use another agents to summarize and translate the summary.",
    tools=[
        FileSearchTool().definitions[0],  # Add this line to enable file search
        connected_agent_summarify.definitions[0],
        connected_agent_translate.definitions[0]
    ],
)

 
DATA_DIR = r"users/tomazkastrun/documents"

os.makedirs(DATA_DIR, exist_ok=True)
output_file = os.path.join(DATA_DIR, "test_html_PS.html")
print(f"Reading / opening the {output_file}...")

 
thread = project_client.threads.create()
print(f"Created thread, thread ID: {thread.id}")

message_file = project_client.files.upload_and_poll(
    file_path=output_file, purpose=FilePurpose.AGENTS
)

 
# Create a message with the file search attachment
# Notice that vector store is created temporarily when using attachments with a default expiration policy of seven days.
attachment = MessageAttachment(file_id=message_file.id,
                               tools=[FileSearchTool().definitions[0]])

 
prompt = "Summarize this document in three lines."
message = project_client.messages.create(thread_id=thread.id,
                                               role="user",
                                               content=prompt,
                                               attachments=[attachment])

print(f"Created message, message ID: {message.id}")
run = project_client.runs.create_and_process(thread_id=thread.id, agent_id=orchestrator_agent.id)
print(f"Created run, run ID: {run.id}")

 

messages = project_client.messages.list(thread_id=thread.id)
print(f"Messages: {messages}")

# get all msgs 
messages = project_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)

for msg in messages:
    if msg.text_messages:
        last_text = msg.text_messages[-1]
        print(f"{msg.role}: {last_text.text.value}")
