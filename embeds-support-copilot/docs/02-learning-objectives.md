# Learning Objectives

Each concept below includes a beginner explanation, why it matters, implementation phase, exercise, and success criterion.

## LLM Fundamentals

| Concept | Beginner explanation | Why it matters | Phase | Practical exercise | Success criterion |
|---|---|---|---|---|---|
| Tokens | Text pieces processed by a model. | Limits prompt size and cost. | Week 1 | Count tokens for a support question plus context. | You can estimate whether context fits. |
| Context windows | Maximum tokens a model can read at once. | Retrieved chunks must fit. | Week 1 | Compare small and large contexts. | You avoid stuffing every document into prompts. |
| Prompts | Instructions and input sent to a model. | Controls answer style and grounding. | Week 1 | Write a grounded-answer prompt. | Answers cite sources and avoid guesses. |
| Structured output | Machine-readable responses such as JSON. | Needed for routing and tools. | Week 1 | Ask for an intent JSON object. | JSON parses without repair. |
| Temperature | Randomness setting for generation. | Lower values help support consistency. | Week 1 | Compare answer variance at two settings. | You choose a stable setting for tests. |
| Hallucinations | Plausible but unsupported claims. | Dangerous in policy support. | Week 1 | Ask unsupported policy questions. | The assistant refuses unsupported claims. |

## RAG Fundamentals

| Concept | Beginner explanation | Why it matters | Phase | Practical exercise | Success criterion |
|---|---|---|---|---|---|
| Documents | Source files used as knowledge. | Policies live here. | Week 2 | Load Markdown policy files. | Each document has metadata. |
| Chunks | Smaller pieces of documents. | Retrieval works over chunks. | Week 2 | Split one policy by headings. | Chunks remain understandable. |
| Embeddings | Numeric vectors representing meaning. | Enables semantic search. | Week 3 | Embed sample questions and chunks. | Related text has nearby vectors. |
| Vector databases | Stores vectors and metadata. | Qdrant holds searchable chunks. | Week 3 | Insert and query chunks. | Relevant chunks return for common questions. |
| Semantic similarity | Meaning-based matching. | Handles paraphrases. | Week 3 | Test paraphrased refund questions. | Correct refund chunks are retrieved. |
| Retrieval | Finding relevant evidence. | Provides context for answers. | Week 3 | Implement top-k search. | Recall@3 reaches target on easy cases. |
| Context construction | Building model input from evidence. | Prevents noisy prompts. | Week 3 | Format chunk text with citations. | Prompt includes sources clearly. |
| Grounded generation | Answering only from evidence. | Reduces hallucination. | Week 3 | Ask answerable and unanswerable questions. | Unanswerable questions are refused. |
| Citations | Source references for claims. | Supports trust and debugging. | Week 3 | Return file names with answers. | Every policy claim has a source. |

## Advanced Retrieval

| Concept | Beginner explanation | Why it matters | Phase | Practical exercise | Success criterion |
|---|---|---|---|---|---|
| Dense retrieval | Embedding-based retrieval. | Good for paraphrases. | Week 3 | Run vector search. | Direct questions retrieve right docs. |
| Sparse retrieval | Keyword-based retrieval. | Good for exact words and IDs. | Week 5 | Add BM25 over chunks. | Exact terms improve ranking. |
| BM25 | Classic keyword ranking method. | Strong baseline for support docs. | Week 5 | Compare BM25 with embeddings. | You can explain wins/losses. |
| Hybrid retrieval | Combines dense and sparse. | Covers meaning and keywords. | Week 5 | Fuse dense and BM25 lists. | Recall improves over dense-only. |
| Reciprocal Rank Fusion | Combines ranked lists by position. | Simple robust fusion method. | Week 5 | Implement RRF in tests. | Hybrid ranking is deterministic. |
| Metadata filtering | Restricting search by fields. | Narrows payments, refunds, owners. | Week 4 | Filter by category. | Filtered results match category. |
| Reranking | Re-sorting candidates with stronger model. | Improves top results. | Week 6 | Rerank top 20 to top 5. | MRR improves on validation set. |
| Query rewriting | Clarifying a user question. | Helps vague or conversational queries. | Week 6 | Rewrite "what about refund?" using history. | Rewritten query retrieves right docs. |
| Multi-query retrieval | Uses several query variants. | Improves recall. | Week 6 | Generate three variants. | At least one finds correct chunk. |
| Query decomposition | Splits complex questions. | Handles multi-part support issues. | Week 6 | Split cancellation plus refund question. | Both relevant docs are retrieved. |
| Parent-child retrieval | Search small chunks, return larger parent context. | Preserves context. | Week 6 | Map child chunks to sections. | Answers include complete section evidence. |

## LangChain

| Concept | Beginner explanation | Why it matters | Phase | Practical exercise | Success criterion |
|---|---|---|---|---|---|
| Document objects | Text plus metadata containers. | Standard ingestion shape. | Week 2 | Represent Markdown as documents. | Metadata survives splitting. |
| Document loaders | Load external files into documents. | Starts ingestion. | Week 2 | Load Markdown files. | File path and title are captured. |
| Text splitters | Split text into chunks. | Controls retrieval quality. | Week 2 | Try heading-aware splitting. | Chunks are neither tiny nor bloated. |
| Embedding integrations | Connect embedding models. | Converts text to vectors. | Week 3 | Embed sample chunks. | Dimensions are consistent. |
| Vector-store integrations | Connect Qdrant. | Stores retrievable vectors. | Week 3 | Insert and search Qdrant. | Top-k retrieval works. |
| Retrievers | Search interface for chains. | Encapsulates retrieval. | Week 3 | Build dense retriever. | It returns documents with scores. |
| Prompt templates | Reusable prompt structures. | Keeps prompts versioned. | Week 3 | Create answer prompt template. | Inputs are explicit. |
| Structured output | Typed model response. | Needed for route decisions. | Week 8 | Validate route JSON. | Invalid output is detected. |
| Tools | Callable functions for external data. | Needed for booking/payment status. | Week 10 | Design read-only tool interface. | Tool input validation passes. |
| Runnable composition | Connecting model/retriever steps. | Builds maintainable chains. | Week 3 | Compose retrieval and answer steps. | Each step can be tested. |

## LangGraph

| Concept | Beginner explanation | Why it matters | Phase | Practical exercise | Success criterion |
|---|---|---|---|---|---|
| State | Shared data passed through graph. | Tracks question, route, evidence, tools. | Week 8 | Draft state schema. | Every node has clear inputs. |
| Nodes | Units of work. | Separates classification, retrieval, tools. | Week 8 | Define node contracts. | Nodes can be tested alone. |
| Edges | Connections between nodes. | Controls flow. | Week 8 | Draw simple RAG route. | Graph path is understandable. |
| Conditional edges | Branches based on state. | Routes to RAG/tools/escalation. | Week 8 | Route booking status to tool. | Expected route is selected. |
| Reducers | Merge state updates. | Handles accumulated messages/evidence. | Week 9 | Design evidence reducer. | No evidence is accidentally overwritten. |
| Loops | Repeated steps. | Enables retries and correction. | Week 9 | Retry weak evidence once. | Loop stops at max retries. |
| Persistence | Saving graph state. | Supports long conversations. | Week 11 | Store conversation checkpoints. | Conversation resumes correctly. |
| Checkpoints | Saved intermediate graph state. | Debug and recover. | Week 11 | Save before tool call. | Failed calls can be inspected. |
| Human-in-the-loop | Human approval or review. | Needed for disputes. | Week 11 | Escalate refund dispute. | Human review receives context. |
| Streaming | Returning partial output. | Improves UX. | Week 15 | Stream final answer tokens. | Client receives incremental text. |
| Error recovery | Handling failures. | Prevents brittle workflows. | Week 9 | Simulate tool timeout. | User gets safe fallback. |

## Fine-Tuning

| Concept | Beginner explanation | Why it matters | Phase | Practical exercise | Success criterion |
|---|---|---|---|---|---|
| Supervised fine-tuning | Training on input-output examples. | Teaches behavior patterns. | Week 12 | Label 30 route examples. | Labels are consistent. |
| LoRA | Small trainable adapter weights. | Reduces training cost. | Week 13 | Read adapter config docs. | You know target modules. |
| QLoRA | LoRA with quantized base model. | Enables training on smaller GPUs. | Week 13 | Estimate memory needs. | Model fits target hardware. |
| Quantization | Lower precision model weights. | Reduces memory. | Week 13 | Compare 16-bit vs 4-bit sizes. | You can explain tradeoffs. |
| NF4 | 4-bit quantization format. | Common QLoRA choice. | Week 13 | Read NF4 config. | You know when it is used. |
| PEFT | Parameter-efficient fine-tuning library. | Provides LoRA adapters. | Week 13 | Create adapter plan. | Adapter saving is understood. |
| TRL | Training library for LLM alignment tasks. | Useful for SFT workflows. | Week 13 | Inspect SFT trainer inputs. | Dataset format is compatible. |
| Training datasets | Examples used to train. | Quality controls behavior. | Week 12 | Build small reviewed JSONL set. | No policy facts are baked in. |
| Splits | Train/validation/test partitions. | Measures generalization. | Week 12 | Split examples by scenario. | Similar examples do not leak. |
| Overfitting | Memorizing training data. | Hurts real performance. | Week 14 | Compare train vs validation. | Gap is explained. |
| Data leakage | Test answers leaking into training. | Invalidates evaluation. | Week 12 | Audit duplicate cases. | Held-out tests remain unseen. |
| Model evaluation | Measuring behavior. | Proves whether training helped. | Week 14 | Compare base vs adapter. | Tool-selection accuracy improves. |

