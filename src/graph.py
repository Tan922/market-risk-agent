from langgraph.graph import StateGraph, MessagesState, START, END

# Simple LangGraph nodes implemented as callables for demo
def decide_retrieve(state: MessagesState):
    last = state.messages[-1]["content"]
    need = any(w in last.lower() for w in ["why", "explain", "summary", "recent", "context"])
    return {"need_retrieval": need}

def retrieve_context(state: MessagesState):
    # Expected: state has a 'retriever' attribute injected externally (FaissStore)
    q = state.messages[-1]["content"]
    retriever = getattr(state, "retriever", None)
    if retriever is None:
        return {"retrieved_docs": []}
    scores, docs = retriever.query(q, k=5)
    return {"retrieved_docs": docs, "retrieval_scores": scores}

def call_llm_node(state: MessagesState):
    # State should have 'llm' injected externally
    prompt_user = state.messages[-1]["content"]
    retr_docs = getattr(state, "retrieved_docs", []) or []
    ctx_texts = "\n\n".join(d.get("text", "") for d in retr_docs)
    prompt = f"You are a market risk analyst assistant. Use context when present.\n\nContext:\n{ctx_texts}\n\nQuery:\n{prompt_user}\n\nProduce a concise multi-sentence summary, a one-word sentiment (bullish/bearish/neutral), and a confidence score between 0 and 1."
    llm = getattr(state, "llm", None)
    if llm is None:
        return {"aiSummary": "LLM not configured", "aiSentiment": "neutral", "aiConfidenceScore": 0.0}
    out = llm(prompt)
    # Very naive parse: we return the raw output as aiSummary
    return {"aiSummary": out, "aiSentiment": "neutral", "aiConfidenceScore": 0.75}

def build_graph():
    graph = StateGraph(MessagesState)
    graph.add_node(decide_retrieve, name="decide_retrieve")
    graph.add_node(retrieve_context, name="retrieve_context")
    graph.add_node(call_llm_node, name="call_llm_node")
    graph.add_edge(START, "decide_retrieve")
    graph.add_edge("decide_retrieve", "retrieve_context", condition=lambda s: s.need_retrieval)
    graph.add_edge("decide_retrieve", "call_llm_node", condition=lambda s: not s.need_retrieval)
    graph.add_edge("retrieve_context", "call_llm_node")
    graph.add_edge("call_llm_node", END)
    return graph.compile()
