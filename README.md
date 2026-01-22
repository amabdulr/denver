# Cisco Documentation Assistant

A Streamlit-based application that analyzes Cisco bug reports and suggests documentation updates using LangChain and RAG (Retrieval-Augmented Generation).

## Features

- **Bug Analysis**: Retrieve and analyze Cisco bug reports
- **First Draft**: Generate documentation drafts based on bug analysis
- **Convert to XML**: Transform content into DITA XML format
- **Hallucination Check**: Verify generated content against source documents

## Prerequisites

- Python 3.8+
- OpenAI API key
- Cisco Bug API credentials

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Denver
```

### 2. Create Virtual Environment

```bash
python3 -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Set Up Knowledge Documents

**Important**: The `knowledge_docs/` folder is excluded from Git due to its size (387 MB).

Create the following directory structure and add your Cisco product documentation PDFs:

```
knowledge_docs/
├── 9800/              # Cisco Catalyst 9800 documentation
├── ASR9000/           # ASR 9000 Series documentation
├── Cisco8000/         # Cisco 8000 Series documentation
├── firepower/         # Firepower documentation
├── pickle_fish/       # Additional documentation
└── sdwan/             # SD-WAN documentation
```

**Where to get the documents**:
- Internal Cisco documentation repositories
- Ask your team lead for access to the documentation package
- Alternatively, configure the path in your environment

### 6. Run the Application

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
Denver/
├── streamlit_app.py           # Main application entry point
├── app_functions.py           # Core agent and utility functions
├── first_draft_tab.py         # First draft generation tab
├── hal_check_tab.py           # Hallucination checking tab
├── Convert.py                 # XML conversion functionality
├── bug2.py                    # Cisco Bug API integration
├── utils.py                   # Shared utility functions
├── requirements.txt           # Python dependencies
├── templates/                 # DITA XML templates
│   ├── ct-concept.xml
│   ├── ct-task.xml
│   ├── ct-reference.xml
│   └── ...
└── knowledge_docs/           # Documentation PDFs (not in Git)
```

## Usage

1. **Bug Search**: Enter a Cisco bug ID to retrieve bug details
2. **Generate First Draft**: Analyze the bug and generate documentation
3. **Convert to XML**: Transform drafts into DITA XML format
4. **Check for Hallucinations**: Verify content accuracy

## Dependencies

Key libraries used:
- `streamlit` - Web application framework
- `langchain` - LLM orchestration
- `chromadb` - Vector database
- `sentence-transformers` - Embeddings
- `python-docx` - Word document handling

See [requirements.txt](requirements.txt) for the complete list.

## Configuration

The application uses:
- **ChromaDB** for vector storage
- **OpenAI embeddings** for document similarity
- **LangChain** for LLM orchestration

## Notes

- Ensure you have valid Cisco API credentials for bug retrieval
- The `auth_token_cache.json` file is auto-generated and excluded from Git
- Data folder contents are excluded from version control

## Troubleshooting

**Issue**: Missing knowledge_docs folder
- **Solution**: Create the folder and add documentation PDFs as described above

**Issue**: OpenAI API errors
- **Solution**: Verify your API key in the `.env` file

**Issue**: Streamlit not starting
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

Internal Cisco project - confidential
