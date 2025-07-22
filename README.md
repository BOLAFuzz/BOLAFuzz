# BOLAFuzz

**Note**: Due to confidentiality agreements and sensitivity requirements, most of the original data obtained in this research cannot be shared. However, we have shared some de-identified data for subsequent research use.

BOLAFuzz is a professional web application security testing tool specifically designed for detecting BOLA (Broken Object Level Authorization, also known as IDOR - Insecure Direct Object References) vulnerabilities. This tool combines automated fuzzing, intelligent crawling, and AI-assisted analysis to effectively identify access control flaws in web applications.

## ✨ Features

- 🎯 **Professional BOLA/IDOR Vulnerability Detection**: Specifically optimized for object-level access control vulnerabilities
- 🤖 **AI-Driven Intelligent Analysis**: Integrated large language models for response difference analysis
- 🕷️ **Automated Crawler**: Supports automatic login and page traversal
- 🔧 **Multiple Fuzzing Strategies**: Including intelligent mutation of path parameters, query parameters, and request body parameters
- 📊 **Detailed Test Reports**: Generates HTML format visualization test reports
- 🐳 **Docker Integration**: Supports Docker environment for isolated testing
- 🎨 **Friendly Command Line Interface**: Provides interactive command line operation experience

## 🔧 System Requirements

- Python 3.8+
- Docker (optional, for isolated testing environment)
- Chrome/Chromium browser (for crawler functionality)

## 📦 Installation

### Clone the Project

```bash
git clone https://github.com/BOLAFuzz/BOLAFuzz.git
cd BOLAFuzz
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure ChromeDriver

The tool includes ChromeDriver. To update if needed:

```bash
# Download the corresponding version of ChromeDriver to crawler/bin/ directory
wget -O crawler/bin/chromedriver https://chromedriver.storage.googleapis.com/xxx/chromedriver_mac64.zip
chmod +x crawler/bin/chromedriver
```

## 🚀 Testing Process

1. **Automatic Login**: The tool will automatically log into the target application using configured credentials
2. **Page Crawling**: Automatically traverse application pages and collect HTTP requests
3. **Parameter Identification**: Intelligently identify parameters that may have BOLA vulnerabilities
4. **Fuzzing**: Perform mutation testing on identified parameters
5. **Difference Analysis**: Use AI models to analyze response differences
6. **Report Generation**: Generate detailed HTML test reports

## 🏗️ Project Structure

```
BOLAFuzz/
├── main.py                    # Main program entry point
├── setup.py                   # Package setup file
├── LICENSE                    # MIT License
├── .gitignore                 # Git ignore file
├── config/                    # Configuration files
│   ├── config.yml             # Main configuration file
│   └── websites.yaml          # Website-specific configurations
├── src/                       # Source code directory
│   ├── __init__.py            # Package initialization
│   ├── core/                  # Core modules
│   │   ├── __init__.py
│   │   ├── init.py            # Initialization module
│   │   ├── startfuzz.py       # Main fuzzing logic
│   │   ├── get_info.py        # Auto-login and info gathering
│   │   ├── selenium_script.py # Selenium automation
│   │   └── mitm_script.py     # Man-in-the-middle proxy
│   ├── fuzzing/               # Fuzzing modules
│   │   ├── __init__.py
│   │   ├── fuzz_script.py     # Core fuzzing script
│   │   ├── param.py           # Parameter handling
│   │   └── diffreq.py         # Request difference analysis
│   ├── analysis/              # Analysis modules
│   │   ├── __init__.py
│   │   ├── chat.py            # Chat-based analysis
│   │   ├── llm_script.py      # LLM analysis script
│   │   ├── simhash.py         # Similarity hashing
│   │   ├── bert_script.py     # BERT-based analysis
│   │   └── train.py           # Model training
│   ├── reporting/             # Report generation
│   │   ├── __init__.py
│   │   ├── makehtml.py        # HTML report generator
│   │   └── make_res.py        # Result processing
│   └── utils/                 # Utility modules
│       ├── __init__.py
│       ├── config.py          # Configuration parsing
│       ├── getmsg.py          # Message processing
│       ├── deduplication.py   # Deduplication algorithms
│       ├── ocr.py             # OCR functionality
│       ├── Node.py            # Node data structure
│       ├── data_script.py     # Data processing
│       ├── json2graph.py      # JSON to graph conversion
│       └── simulate.py        # Simulation utilities
├── crawler/                   # Legacy crawler files
│   ├── bin/                   # Binary files
│   │   ├── chromedriver       # Chrome WebDriver
│   │   ├── LICENSE.chromedriver
│   │   └── THIRD_PARTY_NOTICES.chromedriver
│   ├── config/                # Legacy config files
│   ├── main.py                # Crawler main program
│   ├── conf.py                # Configuration
│   ├── init.py                # Initialization
│   ├── test.json              # Test data
│   └── simulate.py            # Simulation script
├── data/                      # Data files
│   ├── dictionaries/          # Fuzzing dictionaries
│   │   └── dict1.txt          # Default dictionary
│   └── models/                # ML models
│       └── model_full.pth     # Pre-trained model
├── tests/                     # Test files
│   ├── demo.py                # Demo script
│   ├── crawler_demo.py        # Crawler demo
│   ├── test.py                # General tests
│   └── nlp_test.py            # NLP tests
├── outputs/                   # Output files
├── req/                       # Requirements
│   ├── requirements.txt       # Python dependencies
│   ├── dev-requirements.txt   # Development dependencies
│   ├── req1.txt               # Request samples
│   └── req2.txt               # Additional samples
├── docs/                      # Documentation
└── nlp/                       # Legacy NLP directory
```

## 🔬 Technical Principles

### BOLA Vulnerability Detection Principle

1. **Multi-user Comparison**: Use users with different permissions to access the same resource
2. **Parameter Mutation**: Intelligently mutate URL paths, query parameters, and request body parameters
3. **Response Analysis**: Use AI models to analyze response differences and identify potential access control bypasses
4. **Pattern Recognition**: Use machine learning models to identify common vulnerability patterns

### AI-Assisted Analysis

- Use large language models (LLM) to analyze HTTP response differences
- Support local deployment (Ollama) and cloud APIs
- Intelligently identify false positives and false negatives

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

BOLAFuzz is for authorized security testing only. Please ensure you have permission to perform security testing on target applications. Using this tool for unauthorized testing is illegal, and the developers assume no responsibility.
