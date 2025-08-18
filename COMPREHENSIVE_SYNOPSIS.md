# 🌾 IndicAgri: Comprehensive Agricultural Intelligence Platform

## Abstract

IndicAgri is a sophisticated agricultural intelligence platform specifically designed for Indian farming communities, integrating cutting-edge AI technologies with comprehensive agricultural knowledge dissemination. The platform employs a multi-agent architecture powered by Ollama's gemma3:1b model, enabling real-time web search capabilities and contextual agricultural guidance through an intuitive text-based interface.

The system features specialized agricultural agents including crop specialists, disease experts, climate researchers, economics analysts, technology advisors, and policy analysts, each providing domain-specific insights with comprehensive source attribution. The platform's advanced voice transcription infrastructure is designed to support 10 major Indian languages (Hindi, Marathi, Bengali, Telugu, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia) using AI4Bharat's Conformer models, NeMo toolkit, and IndicTrans2 translation pipeline, with foundational voice processing capabilities currently implemented.

IndicAgri's Dataset Creation System employs dual methodologies for comprehensive knowledge acquisition: keyword-based systematic search targeting specific agricultural domains, and autonomous agentic search using intelligent agents that adaptively generate queries. This approach has successfully compiled extensive agricultural datasets covering Indian farming practices, crop management, soil science, climate adaptation, and economic policies. The platform includes sophisticated BM25 retrieval systems for rapid similarity search (24GB indexed data) and state-of-the-art embedding generation using Qwen3-Embedding-8B models with FAISS indexing for semantic search capabilities.

The platform features robust production-ready infrastructure with automated installation scripts, virtual environment management, comprehensive error handling, and modular architecture supporting both detailed analytical responses and concise practical advice modes. Real-time citation generation with inline source attribution ensures information credibility. IndicAgri represents a significant advancement in accessible agricultural technology, providing a scalable foundation for bridging the digital divide for Indian farmers while maintaining scientific rigor through its advanced retrieval-augmented generation pipeline.

---

*Built with Python, Flask, Ollama, NeMo, IndicTrans2, and modern ML frameworks • MIT License • Production Ready*
