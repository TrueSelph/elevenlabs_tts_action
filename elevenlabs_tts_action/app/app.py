"""
This module provides the application logic for integrating ElevenLabs TTS models.

It sets up the UI for model and voice selection and manages API key input
and session state.
"""

import streamlit as st
from jvcli.client.lib.utils import call_action_walker_exec
from jvcli.client.lib.widgets import app_header, app_update_action
from streamlit_router import StreamlitRouter


def render(router: StreamlitRouter, agent_id: str, action_id: str, info: dict) -> None:
    """
    Render the application UI components.

    Args:
        router (StreamlitRouter): The Streamlit router instance.
        agent_id (str): The ID of the agent.
        action_id (str): The ID of the action.
        info (dict): Additional information for rendering.
    """
    # Add app header controls
    model_key, module_root = app_header(agent_id, action_id, info)

    # Add app main controls
    if "elevenlabs_models" not in st.session_state:
        st.session_state["elevenlabs_models"] = call_action_walker_exec(
            agent_id, module_root, "get_models"
        )

    if "elevenlabs_voices" not in st.session_state:
        result = call_action_walker_exec(agent_id, module_root, "get_voices")
        st.session_state["elevenlabs_voices"] = result.get("voices", result)

    # Create dictionaries to map descriptions to IDs
    model_info_dict = {
        f"{model['name']} - {model['description']}": model["model_id"]
        for model in st.session_state["elevenlabs_models"]
    }
    voice_info_dict = {
        f"{voice['name']}": voice["voice_id"]
        for voice in st.session_state["elevenlabs_voices"]
    }

    # Initialize session state for model
    if not st.session_state[model_key].get("model"):
        st.session_state[model_key]["model"] = st.session_state["elevenlabs_models"][0][
            "model_id"
        ]

    # Initialize session state for voice
    if not st.session_state[model_key].get("voice"):
        st.session_state[model_key]["voice"] = st.session_state["elevenlabs_voices"][0][
            "name"
        ]

    # API Key input
    st.session_state[model_key]["api_key"] = st.text_input(
        "API Key", value=st.session_state[model_key]["api_key"], type="password"
    )

    # Model selection
    selected_model_info = st.selectbox(
        "Text-to-Speech Model:",
        options=list(model_info_dict.keys()),
        index=list(model_info_dict.values()).index(
            st.session_state[model_key]["model"]
        ),
    )

    # Voice selection
    selected_voice_info = st.selectbox(
        "Voice:",
        options=list(voice_info_dict.keys()),
        index=list(voice_info_dict.keys()).index(st.session_state[model_key]["voice"]),
    )

    # Update session state with selected model and voice
    st.session_state[model_key]["model"] = model_info_dict[selected_model_info]
    st.session_state[model_key]["voice"] = selected_voice_info

    # Add update button to apply changes
    app_update_action(agent_id, action_id)
