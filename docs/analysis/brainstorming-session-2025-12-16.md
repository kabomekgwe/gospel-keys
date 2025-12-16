---
stepsCompleted: [1]
inputDocuments: []
session_topic: 'Improve backend logic for new AI models'
session_goals: 'Analyze API and brainstorm improvements for backend logic to support multiple/new AI models'
selected_approach: ''
techniques_used: []
ideas_generated: []
context_file: ''
---

# Brainstorming Session Results

**Facilitator:** Kabo
**Date:** 2025-12-16

## Session Overview

**Topic:** Improve backend logic for new AI models
**Goals:** Analyze API and brainstorm improvements for backend logic to support multiple/new AI models

### Session Setup

**Context Analysis:**
The user wants to improve the backend logic to better support "more ai models".
I have analyzed the current implementation:
- **Routes (`ai.py`):** Endpoints are tightly coupled to specific services (`ai_generator_service`, `theory_service`, `midi_service`).
- **Schemas (`ai.py`):** `ProgressionRequest` models have some fields for customization (`ai_percentage`, `creativity`), but don't seem to explicitly support dynamic model selection per request in a flexible way (though `model` defaults might exist in service logic).
- **RAG (`rag_service.py`):** Uses ChromaDB with default embeddings.

**Objective:**
Brainstorm architectural changes or logic improvements to handle a multi-model environment efficiently (e.g., model router, strategy pattern, unified interface, fallback mechanisms).
