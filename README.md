#  Campus Knowledge Engine - AI-Powered Campus Assistant

##  Overview
**Campus Knowledge Engine** is an intelligent **AI-powered campus knowledge system** designed to help students and faculty effortlessly access university information. The platform enables users to **query university documents using natural language conversations**, providing instant answers about courses, admissions, policies, and campus facilities.

Built with **Python, Streamlit, LangChain, and OpenAI API** for the **frontend and AI processing**, along with **Pinecone for vector embeddings** and **SQLite for document storage**, **Campus Knowledge Engine ensures accuracy, efficiency, and 24/7 availability**.
<br>

----
----

##  Features
 **User & Admin Authentication**
- **Student/Faculty Login:** Secure access for campus users.
- **Admin Portal:** Manage documents and system settings.

 **Natural Language Q&A** – Ask questions in plain English and get instant answers.

 **Smart Document Search** – AI-powered search across course catalogs, admission guides, and policies.

 **Retrieval-Augmented Generation (RAG)** – Combines LLM intelligence with document retrieval for accurate responses.

 **User-Friendly Interface** – Clean, intuitive Streamlit-based web application.

 **24/7 Digital Assistant** – Always available to help current and prospective students.

 **Chat History** – View past conversations and questions.

---

##  Technologies Used
- **Frontend:** Streamlit, HTML, CSS
- **AI/ML:** LangChain, OpenAI API (GPT models)
- **Vector Database:** Pinecone (for semantic search)
- **Database:** SQLite
- **Backend:** Python

---

##  Screenshots of the Project

###  Login Page

![WhatsApp Image 2025-09-22 at 22 50 40_842fe0ea](https://github.com/user-attachments/assets/645063ab-56af-4159-9689-da67af079ca3)

*Secure authentication for students and faculty*
<br><br>

---
###  Dashboard

![WhatsApp Image 2025-09-22 at 22 51 17_42586e9c](https://github.com/user-attachments/assets/2fbe330f-7856-4157-909a-486c8d4a2cc6)
*Main interface showing the CollegeBot ready to answer questions*
<br><br>

---
###  Chat Interface

![WhatsApp Image 2025-09-22 at 22 51 29_04a4ba49](https://github.com/user-attachments/assets/8f76190d-dc2e-4950-9500-cb1ffe3afb84)
*Natural language conversation with AI assistant*
<br><br>

---
###  Query Results

![WhatsApp Image 2025-09-22 at 22 51 16_d3e408cc](https://github.com/user-attachments/assets/0d686fda-e004-4b47-9f06-2f4466e45b96)
*AI-powered answers with relevant information from university documents*
<br><br>

---
###  User Profile Page

![WhatsApp Image 2025-09-22 at 22 51 18_ba350ebe](https://github.com/user-attachments/assets/d3b507db-ee4f-4258-b264-ca4a997369a6)

*Manage your profile*
<br><br>

----

<br>

##  Future Plans
 Implement **multi-language support** for international students.  
 Add **voice-based queries** using speech recognition.  
 Integrate **real-time notifications** for important campus updates.  
 Expand to include **course recommendations** based on student interests.  
 Develop **mobile applications** for iOS and Android.  
 Add **analytics dashboard** for tracking popular queries and system usage.

 **Stay tuned for updates!** 

---

##  How It Works
1. **Upload Documents:** Administrators upload university documents (PDFs, course catalogs, policy handbooks)
2. **Vector Embeddings:** Documents are processed and converted into vector embeddings using OpenAI and stored in Pinecone
3. **Query Processing:** Students ask questions in natural language
4. **RAG Pipeline:** The system retrieves relevant document sections and generates accurate answers using GPT
5. **Response Delivery:** Users receive contextual, accurate answers instantly

---

##  Installation & Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/campus-knowledge-engine.git
cd campus-knowledge-engine

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file with:
# OPENAI_API_KEY=your_openai_key
# PINECONE_API_KEY=your_pinecone_key


# Run the application
streamlit run app.py
```




**Built with love for smarter campuses**
