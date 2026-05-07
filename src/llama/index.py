from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings
from langchain_openai import ChatOpenAI

# LLM config
Settings.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Load all markdown files
documents = SimpleDirectoryReader("skills", recursive=True).load_data()

# Create index
index = VectorStoreIndex.from_documents(documents)

# Query engine
query_engine = index.as_query_engine()