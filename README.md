# 🤖 AI Sheets - Simple HTML-Based AI Spreadsheet

A lightweight, HTML-based spreadsheet application that integrates OpenAI's GPT models and web search capabilities. Built with simple HTML/CSS/JavaScript for maximum compatibility and ease of deployment. Perfect for journalists, researchers, data analysts, and anyone who wants to apply AI to their data analysis tasks without complex setup.

<img width="700" height="400" alt="chrome_kOmtjL3szT" src="https://github.com/user-attachments/assets/ba586afe-faa5-40e0-ae8d-b43aae5b1fc8" />
<img width="700" height="400" alt="chrome_msNh1NEKUB" src="https://github.com/user-attachments/assets/7cb094aa-09b0-43ee-8936-d4f853b3633f" />


## ✨ Features

### 🧠 AI-Powered Processing
- **OpenAI GPT-4o Integration** - Access to state-of-the-art language models
- **Column-Based Instructions** - Set AI processing rules once, apply to all rows
- **Real-time Processing** - See AI results instantly as you work
- **Individual Cell Regeneration** - Hover over any AI-generated cell to regenerate or edit
- **Quality Indicators** - Confidence scoring and evidence strength for research validity
- **Systematic Validation** - Robust response parsing with fallback handling

### 🌐 Web Search Capabilities
- **Serper API Integration** - Search the web for current information
- **Research Template** - Built-in web search functionality for any topic
- **Enhanced AI Responses** - Combine web search results with AI processing

### 📊 Data Management
- **CSV Import/Export** - Load and save your data seamlessly
- **Excel Export with Quality Indicators** - Professional Excel export with conditional formatting
- **Advanced Search & Filter** - Full-text search with regex support and export capabilities
- **Frozen Headers** - First row and column stay visible while scrolling
- **Horizontal Scrolling** - Navigate large datasets with ease
- **Responsive Design** - Works perfectly on any screen size

### 🎯 Enhanced AI Templates (11 Total)
- **🌍 Text Translation** - Professional language translation with cultural adaptation
- **😊 Sentiment Analysis** - Analyze emotional tone and sentiment with precision
- **🔍 Keyword Extraction** - Extract important terms with smart formatting
- **📝 Text Summarization** - Condense content into actionable insights
- **📂 Data Classification** - Categorize and organize information effectively
- **👥 Entity Extraction** - Find people, organizations, locations, products
- **🧹 Data Cleaning** - Clean and standardize messy data entries
- **💡 Idea Generation** - Generate creative ideas and suggestions
- **🛡️ Content Moderation** - Check content for appropriateness and safety
- **🗣️ Language Detection** - Automatically detect the language of text
- **🌐 Web Research** - Search and summarize current information
- **🏗️ Hierarchical Coding** - Professional qualitative research coding with confidence scoring

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Modern web browser (Chrome, Firefox, Safari, Edge)
- OpenAI API key ([Get yours here](https://platform.openai.com/api-keys))
- Serper API key for web search ([Get yours here](https://serper.dev)) - Optional

### 1. Setup Backend
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Backend Server
```bash
python main.py
```
The backend will start on `http://localhost:8000`

### 3. Open Frontend
Simply open `simple-frontend.html` in your web browser - no build process required!

### 4. Configure API Keys
1. Click the "Config" button in the application
2. Add your OpenAI API key (required)
3. Add your Serper API key (optional, for web search)
4. Keys are stored securely in your browser's local storage

## 💡 Usage Examples

### Basic AI Processing
1. Load or enter your data in the spreadsheet
2. Click on any column header to set up AI instructions
3. Choose from pre-built templates or create custom instructions
4. Select the source column that contains your data
5. Click "Apply Instructions" to process all rows

### Web Search Research
1. Enter topics or queries in a column (e.g., "Tesla stock price", "AI news 2024")
2. Click the column header and select "🌐 Search the web for" template
3. The AI will search the web and provide comprehensive summaries

### Data Translation
1. Enter text in your source language
2. Use the "Translate" template with custom target language
3. Get professional-quality translations for all your data

### Qualitative Research Coding
1. Load interview transcripts or qualitative data
2. Select the "🏗️ Hierarchical Coding" template
3. Configure your column names for different coding levels
4. Get systematic thematic analysis with confidence scoring and evidence assessment
5. Export to Excel with professional formatting and quality indicators

<img width="1693" height="1304" alt="chrome_oNTUgdevAH" src="https://github.com/user-attachments/assets/1cda0a91-52aa-4bac-8171-c5c3500114f0" />


## 🎛️ Interface Features

### Smart Cell Interactions
- **Hover Actions**: Hover over AI-generated cells to see regenerate (🔄) and edit (⚙️) buttons
- **Visual Indicators**: Cells with AI instructions show a blue background and orange border
- **Quality Indicators**: Confidence dots and evidence symbols for research validity
- **One-Click Regeneration**: Instantly regenerate individual cells without reprocessing everything

### Navigation
- **Frozen Headers**: Column names and row numbers stay visible while scrolling
- **Horizontal Scroll Bar**: Navigate wide datasets easily
- **Responsive Sidebar**: Column instruction panel slides in from the right

### Example Templates
Access pre-built examples from the "Examples" menu:
- **Text Classification** - Sentiment analysis of movie reviews
- **Named Entity Recognition** - Extract person names from news articles
- **Data Cleaning** - Normalize messy data entries
- **👥 Entity Extraction** - Extract companies, people, locations from news
- **🔍 Keyword Analysis** - Extract keywords from product descriptions
- **💡 Idea Generation** - Generate marketing ideas from product features
- **Web Search & Research** - Current information on any topic

## 🔧 API Configuration

### Environment Variables (.env file)
```bash
# Required for AI processing
OPENAI_API_KEY=your_openai_api_key_here

# Optional for web search functionality
SERPER_API_KEY=your_serper_api_key_here
```

### Supported Models
- **GPT-4o** - Most capable model with advanced reasoning (default)
- Additional models can be configured in the backend

## 📁 Project Structure

```
sheets/
├── backend/                 # FastAPI Python backend
│   ├── main.py             # API endpoints and web search
│   ├── openai_functions.py # OpenAI integration
│   ├── hf_functions.py     # Hugging Face integration
│   ├── requirements.txt    # Python dependencies
│   └── .env               # API configuration (optional)
├── simple-frontend.html   # Main HTML application (no build required!)
├── test_conversations.csv # Sample data file
├── flow.md               # User flow documentation
├── prd.md                # Product requirements
├── tasks.md              # Development tasks
└── README.md            # This file
```

## 🏗️ Architecture

**Simple HTML Architecture** - No complex frameworks or build processes:
- **Frontend**: Single HTML file with embedded CSS/JavaScript
- **Backend**: FastAPI Python server for AI processing
- **Storage**: Browser localStorage for API keys, in-memory for data
- **Deployment**: Drop the HTML file anywhere, run Python backend

## 🌟 Use Cases

### 📰 Journalism & Media
- Analyze sentiment of social media posts about events
- Extract quotes and key information from interviews
- Translate international news for local audiences
- Research current developments on breaking stories

### 📊 Data Analysis
- Clean and standardize messy survey responses
- Classify customer feedback into categories
- Extract structured data from unstructured text
- Research market trends and competitor information

### 🎯 Marketing & Business
- Analyze customer reviews and feedback sentiment
- Research competitor products and pricing
- Translate marketing materials for global markets
- Extract insights from industry reports

### 🔬 Research & Academia
- **Qualitative Data Analysis** - Systematic hierarchical coding with confidence scoring
- **Literature Review** - Categorize research papers and extract key findings
- **Interview Analysis** - Professional thematic analysis with evidence assessment
- **Survey Research** - Analyze responses with quality indicators and validation
- **Cross-language Research** - Translate and analyze international sources

## 🛠️ Development

### Dependencies
- **Backend**: FastAPI, OpenAI Python SDK, httpx for web requests
- **Frontend**: Pure HTML/CSS/JavaScript with SheetJS for Excel export (no Node.js, no build process!)

### Adding New Templates
1. Update the `templates` object in `simple-frontend.html` (around line 1064)
2. Add the template HTML in the instruction templates section (around line 544)
3. Optionally add example data in the `loadExample()` function (around line 917)

### Creating Additional Pages
Since this is now an HTML-based project, you can easily create additional pages:
- Copy `simple-frontend.html` as a starting template
- Modify for specific use cases (e.g., `keyword-analyzer.html`, `translator.html`)
- All pages can share the same backend API
- No build process or complex deployment required

## 🔒 Security & Privacy

- **Local Processing**: All data stays on your machine
- **Secure API Keys**: Keys are stored locally and transmitted securely
- **No Data Persistence**: Data is only stored in browser memory by default
- **HTTPS Ready**: Backend supports secure connections

## 🤝 Contributing

We welcome contributions! Areas for improvement:
- Additional AI processing templates
- New data import/export formats
- Enhanced UI features
- Performance optimizations
- Documentation improvements

## 📄 License

Open source - feel free to use, modify, and distribute.

---

**🚀 Start analyzing your data with AI in just 5 minutes!**

Get your API keys, load the application, and transform how you work with data using the power of artificial intelligence and web search.
