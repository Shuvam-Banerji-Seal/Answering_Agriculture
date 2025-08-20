
* Aheli Poddar \[Team Lead\]  
* Shuvam Banerji Seal  
* Mishra Alok Ajay

**Project Title:** IndicAgri (Retrieval Augmented Agricultural Platform for India)

## **2\. Theme Details**

**Theme Name:** Exploring and Building Agentic AI Solutions for a High-Impact Area of Society: Agriculture  
**Theme Benefits:**  
  Our chosen theme addresses the critical gap in agricultural technology adoption among Indian farmers by providing intelligent, accessible and culturally-aware digital solutions. This theme effectively supports sellers (agricultural input suppliers, equipment dealers and financial services) by:

* **Enhanced Customer Engagement**: Enabling sellers to provide value-added advisory services through AI-powered recommendations  
* **Market Intelligence**: Real-time insights into crop patterns, seasonal demands and regional agricultural trends  
* **Trust Building**: Scientific, citation-backed recommendations that increase farmer confidence in seller advice  
* **Scalable Reach**: Multi-modal interfaces (voice, text) that overcome literacy and technology barriers  
* **Data Driven Sales**: Analytics on crop cycles, input requirements and optimal selling periods  
* **Competitive Differentiation**: Sellers can offer AI assistance and Real-time data analysis as a premium service differentiator

## **3\. Synopsis**

## **Solution Overview**

**IndicAgri** is a comprehensive, multi-modal AI agricultural chatbot system specifically designed for the Indian agricultural ecosystem. The solution combines Large Language Models (LLMs), Retrieval Augmented Generation (RAG) and real-time data integration(Time-Series Forecasting) to provide farmers with scientifically accurate, region specific and actionable agricultural guidance.  
**Core Capabilities:**

* **Multi-Modal Intelligence**: Processes text queries, voice commands (22 Indian languages), Time Series Forecasting  
* **Comprehensive Agricultural Knowledge**: Covers 100+ crop varieties, soil management, weather patterns, government schemes, market trends etc.  
* **Real-Time Integration**: Live weather data, market prices, government scheme updates and seasonal recommendations  
* **Regional Specialisation**: State and region specific advice tailored to local farming practices, soil types, and climatic conditions   
* **Scientific Accuracy**: All recommendations backed by research articles, agricultural university prints and peer-reviewed sources with inline citations.

## **Technical Stack**

**Core AI & Machine Learning:**

* **Large Language Models**: Using open source local LLMs like Gemma3, DeepSeek for inference and agentic database creation  
* **Embedding Models**: [Qwen3-Embedding-8B](https://huggingface.co/Qwen/Qwen3-Embedding-8B) for vector search and semantic similarity and Okapi-BM25 for keyword-based searching (as a fallback with optimisations for [vague query retrieval](https://trec.nist.gov/pubs/trec33/papers/IISER-K.tot.pdf))  
* **Speech Processing**: [Indic-Conformer](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual) by AI4Bharat  for multi-language voice transliteration   
* **Vector Database**: FAISS/ChromaDB for efficient similarity search across 15,000+ agricultural documents

**Data Integration & Processing:**

* **Web Scraping**: Custom multi-agent system for continuous knowledge base updates  
* **Real-Time APIs**: Weather (IMD, OpenWeatherMap), Market Prices (APMC, e-NAM), Government Schemes  
* **Knowbase Updater:** a Python-based scheduler to automatically scrape the internet for newer resources for our IndicAgri database and update the database vectors  
* **Content Processing**: LangChain for RAG implementation, BeautifulSoup for web scraping and OCR for PDF data extraction. 

**Frontend :**

* **Web Application**: HTML, CSS and JS with Progressive Web App capabilities

**Deployment & Infrastructure *(what we plan to include in future)*:**

* **Containerization**: Docker with multi-stage builds for optimised deployments  
* **Orchestration**: Kubernetes for auto-scaling and service mesh management  
* **Cloud Services**: AWS/Azure for compute, storage, and managed services  
* **CDN**: CloudFront for global content delivery and multimedia optimisation  
* **Monitoring**: Prometheus \+ Grafana for real-time system monitoring and alerts

*(**PS:** Currently, the whole project includes a database containing a huge chunk of the research, news articles, public government documents and query retrieval pipeline, meaning most of the available **free tier hosting is not viable**. What we planned to achieve now is an automated information retrieval system, which can only be run through Dockerized containers. )*

**Open Source Components:**

* **LangChain**: RAG pipeline implementation (FAISS) and LLM orchestration.  
* **Transformers (Hugging Face)**: Qwen3, Gemma3, DeepSeekV3.  
* **STT:** Indic Conformer and GoogleTrans for voice-to-text transliteration.

## **Decision Rationale**

**Architecture Decisions:**

* **Microservices Architecture**: Chosen for scalability, independent deployability, and fault isolation. Each component (NLP, data retrieval) can scale independently based on demand.  
* **RAG over FineTuning**: Selected RAG approach to maintain up-to-date information without expensive model retraining, enabling real-time knowledge updates from agricultural research and government policies.  
* **Keyword Retrieval:** Using BM25 retrieval for more specific queries and also as a fallback.  
* **Multi-Modal Processing**: Essential for Indian agricultural context where farmers have varying literacy levels and prefer voice interactions over text.

**Technology Constraints:**

* **Language Model Selection**: Open sourced Local LLM models like Qwen, Gemma, DeepSeek over closed source implementation or API calls  
* **Regional Language Support**: Currently all 22 Indian Languages are available via the Indic Conformer.  
* **Internet Connectivity**: Designed progressive degradation for areas with poor connectivity, with offline capabilities for core features(limited knowledge update possible if offline)

**Key Assumptions:**

* **Farmer Device Access**: Assuming 70%+ smartphone penetration in target rural areas *(future deployment prospects)*  
* **Data Quality**: Relying on government and institutional data sources for accuracy and timeliness  
* **User Adoption**: Farmers will adopt voice-based interfaces more readily than text-based interactions *(future deployment prospects)*

## **Innovation Highlights**

* SOTA agricultural knowledge base with 15,000+ curated entries specifically for Indian farming. ***We have scraped the sources and made the [IndicAgri dataset](https://huggingface.co/datasets/ShuvBan/IndicAgri) publicly available through [HuggingFace](https://huggingface.co/datasets/ShuvBan/IndicAgri)***  
* **An Agentic Database Creation tool** was developed that gets a config file to look for articles, research documents, etc., and searches through the internet using DuckDuckGo search engine and automatically decides which documents to scrape. *Multiple agents could be deployed at once (we deployed 12 agents)*  
* Dynamic query decomposition that breaks complex farming questions into specialised sub-queries  
* Real-time integration of weather, market and policy data with historical agricultural patterns  
* Voice processing in 22 Indian languages with agricultural terminology understanding  
* Maintains context across extended conversations   
* Proactive recommendations based on seasonal timing and regional conditions

## **Feasibility and User-Friendliness**

**Technical Feasibility:**

* All core technologies are mature and widely adopted  
* Microservices design supports gradual rollout and scaling  
  ***(PS:** Current implementation requires a server-client ecosystem if the project needs to be run on low powered devices through web-interface. The backend needs some decent level of computing power to be feasible for the masses. A simple laptop with 8GB of RAM will be able to handle most of the features provided in our solution.**)***

**User Adoption Potential:** 

* Voice interactions mirror existing user behaviours  
* Native language support reduces adoption barriers  
* Simple queries for beginners, advanced features for experienced farmers

**Economic Viability:**

* Integration with agricultural input suppliers, banks, and cooperatives  
* Potential partnerships with extension services and Krishi Vigyan Kendras  
* Data monetisation by anonymised agricultural insights, which will be valuable for policy makers and agribusinesses

**Operational Efficiency:**

* Continuous learning and knowledge base expansion  
* Self-service capabilities reduce manual intervention requirements  
* Continuous updates from publicly available articles and research documents  
* Supports government digital agriculture initiatives  
* Promotes sustainable farming practices and climate adaptation

# **Success Metrics**

## ***Current Measurable Metrics (Development Stage)***

### **Technical Performance:**

* **Query Response Time**: \<3 seconds for 90% of queries (direct fetch from Database)  
* **Database Coverage**: 15,000+ curated agricultural entries  
* **Multi-language Processing**: 22 Indian languages supported  
* **System Reliability**: 99% successful query processing

### **Knowledge Base Quality:**

* **Source Authority**: 80% citations from government/research institutions  
* **Content Freshness**: Real-time weather and market data integration  
* **Sub-query Generation**: Complex queries broken into 3-5 targeted searches

### **User Adoption *(Future Success Indicators post deployment)*:**

* **Feature Usage**: Adoption of specialised tools (crop recommender, soil analyser)  
* **Geographic Reach**: Active users across states due to language viability  
* **Government Scheme Awareness**: Increased queries about subsidies/schemes  
* **Seasonal Engagement**: Usage spikes during planting/harvesting periods

## 

## **4\. Methodology/Architecture Diagram**

Our comprehensive architecture diagram provides a visual representation of the IndicAgri system's end-to-end flow and component interactions. For more details, please refer our github repository:  [here](https://github.com/Shuvam-Banerji-Seal/Answering_Agriculture).

## 

**Flow Chart: Query Processing Pipeline**  
![][image1]  
   
 For a better overview, please refer to our YouTube video here:[IndicAgri: Multi-Modal Agricultural AI System | Live Demo + Architecture Overview | Team Fibonacci](https://youtu.be/UQ1iJkPihfY?si=yHtrexoIAC63-Ms0)  
   
 **Block Diagram: System Components**

* **Input Layer**: Voice, Text API processing modules  
* **Processing Layer**: NLP engine, Query decomposition, Context management  
* **Knowledge Layer**: Vector database, Real-time APIs, Historical data  
* **Intelligence Layer**: LLM integration, RAG system, Specialized tools  
* **Output Layer**: Multi-format response generation, Channel distribution

**Architecture Diagram Links:**

* **Main System Architecture**: [link](https://github.com/Shuvam-Banerji-Seal/Answering_Agriculture/blob/main/System_arch.png)   
* **Database Generation System**: link  
* **API Documentation Flow**: \[Interactive API Documentation Link\]  
* **Mobile App Wireframes**: \[Mobile Interface Design Links\]

   


