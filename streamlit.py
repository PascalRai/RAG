import streamlit as st
import requests

# Base URL for your FastAPI app
BASE_URL = "http://localhost:8000/api/v1"  # Adjust if needed

st.title("RAG Chat App")

# Ensure session state defaults
if "indexes" not in st.session_state:
    st.session_state["indexes"] = []
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Sidebar for Index Management
st.sidebar.header("Index Management")

# List Indexes
if st.sidebar.button("Refresh Indexes"):
    try:
        response = requests.get(f"{BASE_URL}/indexes")
        if response.status_code == 200:
            indexes = response.json().get("indexes", [])
            st.session_state["indexes"] = indexes
            st.sidebar.write("Available Indexes:")
            for idx in indexes:
                st.sidebar.write(f"- {idx}")
        else:
            st.sidebar.error("Failed to fetch indexes")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# Ingest PDF
st.sidebar.subheader("Ingest PDF")
index_name = st.sidebar.text_input("Index Name")
file_path = st.sidebar.text_input("File Path (on Celery container)")
if st.sidebar.button("Ingest PDF"):
    if index_name and file_path:
        try:
            payload = {"file_path": file_path}
            response = requests.post(f"{BASE_URL}/indexes/{index_name}/pdf", json=payload)
            if response.status_code == 200:
                st.sidebar.success("Ingestion enqueued")
            else:
                st.sidebar.error("Failed to enqueue ingestion")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.warning("Provide index name and file path")

# Tabs for Chat and Retrieval
tab1, tab2 = st.tabs(["Chat", "Retrieval"])

with tab1:
    st.header("Chat with RAG")

    # Select collection
    collection_name = st.selectbox("Select Collection", ["test_01"] + st.session_state.get("indexes", []), key="collection")

    # Display chat history
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    query = st.chat_input("Ask a question...")

    if query:
        # Add and display user message
        st.session_state["messages"].append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        # Non-streaming request to /rag
        try:
            resp = requests.post(
                f"{BASE_URL}/rag",
                params={"query": query, "collection_name": collection_name},
                data=""  # endpoint expects empty body per example
            )
            if resp.status_code == 200:
                resp_json = resp.json()
                assistant_text = resp_json.get("response", "")
                with st.chat_message("assistant"):
                    st.markdown(assistant_text)
                if assistant_text:
                    st.session_state["messages"].append({"role": "assistant", "content": assistant_text})
            else:
                st.error(f"Failed to get response ({resp.status_code})")
        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.header("Retrieval Test")
    ret_query = st.text_input("Query", key="ret_query")
    ret_index = st.selectbox("Index", ["test_01"] + st.session_state.get("indexes", []), key="ret_index")
    top_k = st.slider("Top K", 1, 10, 5)
    if st.button("Retrieve"):
        try:
            payload = {"query": ret_query, "index_name": ret_index, "top_k": top_k}
            response = requests.post(f"{BASE_URL}/retrieve", json=payload)
            if response.status_code == 200:
                results = response.json().get("results", [])
                for res in results:
                    st.write(f"ID: {res['id']}, Score: {res['score']}")
                    st.write(f"Text: {res['text']}")
                    st.write("---")
            else:
                st.error("Failed to retrieve")
        except Exception as e:
            st.error(f"Error: {e}")