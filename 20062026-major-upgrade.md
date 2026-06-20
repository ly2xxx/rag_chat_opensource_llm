# Modernize the RAG solution (LangChain 0.2 → 1.x + Streamlit native)

## Context

`C:\code\rag_chat_opensource_llm_main` is a ~1.5-year-old Streamlit RAG chatbot ("Rob") built on **LangChain 0.2.10** (Nov 2024). Everything still works against a local/cloud Ollama, but the stack is now several major versions behind and leans on deprecated APIs that will break on the next upgrade and that no longer represent how RAG apps are built:

- **Deprecated imports** throughout (`langchain.document_loaders`, `langchain.vectorstores`, `langchain.embeddings`, `langchain.schema`, `langchain_community.chat_models.ChatOllama`, `langchain_community.embeddings.OllamaEmbeddings`).
- **`ConversationalRetrievalChain`** — a deprecated legacy chain. It forces a GPT-2 tokenizer (the manual `models--gpt2` copy hack in the README) just to count tokens.
- **Pickle-serialized FAISS** indexes (`pickle.dump(vectors)`), which is fragile and an insecure-deserialization vector.
- **`st-pages`** + **`streamlit-chat`** — both fully obsoleted by native Streamlit (`st.navigation`/`st.Page`, `st.chat_message`/`st.chat_input`).
- Dead/heavy deps: `pandasai`, explicit `torch`/`transformers`/`tiktoken` pins, `huggingface-hub<0.23` cap (all artifacts of the GPT-2 hack / a commented-out feature).
- Removed-API usage: `st.image(..., use_column_width=True)`.

**Decisions (confirmed with user):** Full modernization (core RAG **and** Streamlit UI); **LCEL retrieval chain** architecture (history-aware retriever, not LangGraph); **native FAISS `save_local`** persistence (replaces the `.pkl` download/zip-merge format).

**Outcome:** same UX and features, running on the current LangChain 1.x + native-Streamlit stack, with deprecated APIs and the GPT-2 hack gone.

## Target dependency set (`pyproject.toml`)

Let `uv` resolve exact versions; specify lower bounds only.

**Add / change:**
- `langchain>=1.0`, `langchain-core>=1.0`, `langchain-community>=0.3`, `langchain-text-splitters>=0.3`
- `langchain-classic>=1.0`  ← provides `create_history_aware_retriever`, `create_retrieval_chain`, `create_stuff_documents_chain` in 1.x
- `langchain-ollama>=0.3`  ← `ChatOllama`, `OllamaEmbeddings`
- `streamlit>=1.40`  (native multipage + chat)
- `sentence-transformers>=3` (for the similarity page)
- `python-dotenv>=1` (sidebar already imports `dotenv`)
- keep: `faiss-cpu`, `pypdf`, `pdfplumber`, `openpyxl`, `bs4`, `requests`

**Remove:** `pandasai`, `torch`, `transformers`, `tiktoken`, `streamlit-chat`, `st-pages`, the `huggingface-hub<0.23.0` cap. (`flask` is only used by the unrelated `flask_app.py` — leave unless it blocks resolution.)

> Risk: community/classic 1.x must co-resolve with core 1.x. Evidence (Feb 2026) shows community 1.1.0 exists, so this should resolve. If `uv sync` hits a conflict, fall back to the still-current 0.3.x line (`langchain~=0.3`, helpers then import from `langchain.chains` instead of `langchain_classic.chains` — the only code delta).

## Code changes

### `modules/embedder.py` — imports + native persistence
- Swap deprecated imports:
  - loaders → `langchain_community.document_loaders` (`CSVLoader`, `PyPDFLoader`, `TextLoader`)
  - `FAISS` → `langchain_community.vectorstores`
  - `OllamaEmbeddings` → `langchain_ollama`
  - `Document` → `langchain_core.documents`
  - `RecursiveCharacterTextSplitter` → `langchain_text_splitters`
  - drop the unused `OpenAIEmbeddings`/`HuggingFaceEmbeddings` imports.
- **Persistence:** replace pickle with native FAISS. `storeDocEmbeds` → `vectors.save_local(f"{PATH}/{safe_model}-{filename}")` (writes `index.faiss` + `index.pkl` into that folder). `getDocEmbeds` → `FAISS.load_local(folder, embeddings, allow_dangerous_deserialization=True)`; treat the **folder's existence** as the "already embedded" check. Set `st.session_state["vectordb"]` to the folder path.
- **Zip merge** (`readVectorsFromZip`): each saved index is now a folder, not a `.pkl`. Iterate sub-folders of the extraction dir, `FAISS.load_local` each, `merge_from` into the accumulator (keep the existing merge logic; only the per-item load changes). Keep `generateEmbeddingsFromFile`'s bytes-or-str handling for web `StringIO` input.
- Move the hardcoded `base_url` to `OLLAMA_BASE_URL` env (default `http://localhost:11434`); keep `nomic-embed-text` as the embed model.

### `modules/chatbot.py` — LCEL retrieval chain (replaces `ConversationalRetrievalChain`)
- `ChatOllama` from `langchain_ollama`; prompts from `langchain_core.prompts` (`ChatPromptTemplate`, `MessagesPlaceholder`).
- Build once per call:
  ```
  history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
  qa_chain  = create_stuff_documents_chain(llm, qa_prompt)   # qa_prompt keeps Robby persona + {context}
  rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)
  result = rag_chain.invoke({"input": query, "chat_history": <list[BaseMessage]>})
  ```
  helpers imported from `langchain_classic.chains` / `langchain_classic.chains.combine_documents`.
- `chat_history` is built from prior turns as `HumanMessage`/`AIMessage` (see history change). Answer = `result["answer"]`; expose `result["context"]` for a Sources expander.
- Delete the `langchain.verbose` hack, the commented `ctransformers`/HF-pipeline block, and the `max_tokens_limit` GPT-2 dependency.

### `modules/history.py` — native chat, single message list
- Drop `from streamlit_chat import message`. Store one `st.session_state["messages"]` list of `{"role","content"}`. `generate_messages` renders with `st.chat_message(role).write(content)`. Add a helper to convert messages → `list[BaseMessage]` for the chain. Keep greeting/reset semantics. Remove the unused file `load`/`save` methods.

### `modules/utils.py` — `setup_conversation_cockpit` rewrite
- Replace the `layout.prompt_form` + stdout-capture flow with: render history, then `if prompt := st.chat_input(...)` → append+render user msg, call `chatbot.conversational_chat`, append+render assistant msg, show retrieved docs in a `st.expander("Sources")` (replacing the old "agent's thoughts" stdout hack). `setup_chatbot` stays but reads the FAISS folder via the updated embedder.

### `modules/layout.py` — remove `prompt_form` (superseded by `st.chat_input`); keep `show_header`.

### `modules/sidebar.py` — modern downloads
- Replace the base64 `<a>` hacks with `st.download_button`. `download_model`: zip the FAISS **folder** (`shutil.make_archive` to a temp file) and offer the zip. `download_conversation`: build text from `st.session_state["messages"]`. Keep model/temperature selectors and `.env` `LLM_MODEL` parsing.

### `streamlit_app.py` — native multipage
- Remove all `st_pages` imports/usage. Define navigation with `st.navigation([st.Page(...), ...])` listing Home + the four feature pages (download.py excluded from nav, matching today's `hide_pages(["download"])`), then `nav.run()`. Fix `st.image(..., use_column_width=True)` → `use_container_width=True`.
- Delete the `.streamlit/` pages-config block that `st-pages` consumed.

### `pages/*.py` (0,1,2,3 + download.py)
- Remove `from st_pages import hide_pages` and the `hide_pages([...])` calls. Remove the `reload_module` dev hack (Streamlit reruns scripts on change). Update calls to the new cockpit/history API. `download.py`: zip-of-folders instead of zip-of-`.pkl`s (the `embeddings/` dir now holds folders); switch its base64 link to `st.download_button`.

### `modules/similarity.py`
- Works as-is with `sentence-transformers>=3`; switch `util.pytorch_cos_sim` → `util.cos_sim` (current name). Imports otherwise unchanged.

## Non-code / housekeeping
- **`Dockerfile`**: repo moved to `uv`, but the Dockerfile still `pip install -r requirements.txt`. Switch to a `uv`-based build (`COPY pyproject.toml uv.lock` → `uv sync --frozen` → `uv run streamlit run ...`).
- **`requirements.txt`** (stale UTF-16, pins LangChain 0.2): regenerate via `uv export --no-hashes -o requirements.txt` so it matches `uv.lock`, or delete if the Dockerfile no longer needs it.
- **`README.md`**: delete the "Setup gpt-2 tokenizer manually" section + screenshot reference; update the capability bullets that name `ConversationalRetrievalChain`; bump the Python prereq note.
- **`uv.lock`**: regenerate via `uv sync`.

## Verification
1. `cd C:\code\rag_chat_opensource_llm_main && uv sync` — resolves the new tree cleanly (this is the gate for the 1.x-vs-0.3.x dependency risk above).
2. `uv run python -c "import modules.embedder, modules.chatbot, modules.utils, modules.history, modules.sidebar, modules.layout, modules.similarity"` — no import errors (catches missed deprecated paths).
3. Ensure Ollama is reachable (`ollama pull nomic-embed-text`; a chat model from `.env` `LLM_MODEL`). `uv run streamlit run streamlit_app.py`.
4. Manual end-to-end:
   - Home page renders via native nav; "download" not shown in the sidebar nav.
   - **Chat-file**: upload a PDF/TXT/CSV/XLSX → ask a question → grounded answer streams into `st.chat_message`; Sources expander lists retrieved chunks; a second question uses chat history (history-aware retriever). Confirm `embeddings/<model>-<file>/index.faiss` is created (not a `.pkl`).
   - **Chat-web** and **Keywords-Research**: load URL(s) → chat works through the same cockpit.
   - **Text-Similarity**: two texts → score returned.
   - Sidebar "Download Trained Model" returns a zip of the FAISS folder; "Download Chat History" returns the transcript.
   - Re-upload the same file → loads existing index (no re-embed).
5. Confirm no `models--gpt2` copy is required to start (GPT-2 hack removed).

## Out of scope
`flask_app.py` (unrelated standalone), the `Gallery/` assets, and any change to the Ollama models themselves.