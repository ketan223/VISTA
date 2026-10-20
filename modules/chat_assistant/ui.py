"""
VISTA AI Chat Assistant - Streamlit UI View
Powered by Google Gemini 3.8 Flash with local Ollama fallback.
"""

import streamlit as st
from modules.chat_assistant.engine import PERSONAS, stream_gemini_chat, stream_ollama_chat, generate_chat_response

def render_chat_assistant_ui():
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #f1f5f9;">
                💬 AI Chat Assistant
            </div>
            <div style="font-size: 0.9rem; color: #94a3b8; margin-top: 0.25rem;">
                Powered by Google Gemini 3.8 Flash with specialized personas & local Ollama fallback.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "Hello! I am your **VISTA AI Chat Assistant**, powered by **Google Gemini 3.8 Flash**.\n\nSelect a persona in the sidebar or ask anything below!",
                "engine": "Google Gemini 3.8 Flash",
            }
        ]

    # Persona selector
    col_persona, col_clear = st.columns([4, 1])
    with col_persona:
        persona_keys = list(PERSONAS.keys())
        persona_names = [f"{PERSONAS[k]['name']} ({PERSONAS[k]['role']})" for k in persona_keys]
        selected_idx = st.selectbox(
            "Active Specialist Persona",
            range(len(persona_keys)),
            format_func=lambda i: persona_names[i],
            key="chat_persona_select",
        )
        current_persona_id = persona_keys[selected_idx]

    with col_clear:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    # Display chat messages
    for msg in st.session_state.chat_history:
        role = msg["role"]
        with st.chat_message(role):
            if role == "assistant" and "engine" in msg:
                st.caption(f"⚡ {msg['engine']}")
            st.markdown(msg["content"])

    # User Input
    user_query = st.chat_input("Ask anything or paste code/ideas here...")
    if user_query:
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate response with live streaming
        with st.chat_message("assistant"):
            persona = PERSONAS.get(current_persona_id, PERSONAS["general"])
            system_prompt = persona["system_prompt"]
            payload = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.chat_history
            ]
            engine_label = ["Google Gemini 3.8 Flash"]

            def stream_gen():
                try:
                    for chunk in stream_gemini_chat(payload, system_prompt, 0.7):
                        yield chunk
                except Exception as e:
                    engine_label[0] = "Local Ollama"
                    try:
                        for chunk in stream_ollama_chat(payload, system_prompt, 0.7):
                            yield chunk
                    except Exception as err:
                        yield f"⚠️ AI Service Error: {str(err)}"

            st.caption(f"⚡ {engine_label[0]}")
            full_reply = st.write_stream(stream_gen())

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": full_reply,
            "engine": engine_label[0],
        })
