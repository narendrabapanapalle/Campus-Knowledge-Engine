📚 Campus Knowledge Engine

An intelligent AI-powered campus knowledge system that allows students and faculty to query university documents — including course catalogs, admission guides, and policies — using natural language conversations.
This acts as a 24/7 digital campus assistant, helping current and prospective students instantly find accurate information.

🚀 Features

⚡ Natural language Q&A over university documents

🧠 Powered by LLM + Retrieval-Augmented Generation (RAG)

🔍 Smart search across policies, course catalogs, and admission booklets

🎓 Designed for students, faculty, and new applicants

🌐 Streamlit web app with clean UI

🔗 Optional vector search using Pinecone

🛠️ Tech Stack

Python

Streamlit

LangChain

OpenAI API

Pinecone (vector embeddings)

SQLite (local document storage)

📁 Project Structure
/campus-knowledge-engine
│── app.py               # Main Streamlit UI
│── rag_pipeline.py      # RAG logic
│── documents/           # University docs
│── embeddings/          # Vector embeddings storage
│── utils/               # Helper functions
│── requirements.txt     # Dependencies
│── README.md            # Documentation

▶️ How to Run

Clone the repository:

git clone <repo-url>
cd campus-knowledge-engine


Install dependencies:

pip install -r requirements.txt


Set your API keys:

export OPENAI_API_KEY="your_key"
export PINECONE_API_KEY="your_key"


Run the app:

streamlit run app.py

🔗 Project Link

(Insert your link here)

🤝 Contributions

Feel free to open issues or submit pull requests.
