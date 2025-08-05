"""
This module provides the application logic for integrating ElevenLabs TTS models.

It sets up the UI for model and voice selection and manages API key input
and session state.
"""

from typing import Optional

import streamlit as st
from jvclient.lib.utils import call_api, call_update_action
from jvclient.lib.widgets import app_header, app_update_action
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
    # --- Step 1: API Key input
    api_key = st.text_input(
        "API Key", value=st.session_state[model_key]["api_key"], type="password"
    )

    if api_key and not st.session_state[model_key]["api_key"]:
        # update the API key once inputted for first time
        st.session_state[model_key]["api_key"] = api_key
        call_update_action(
            agent_id=agent_id,
            action_id=action_id,
            action_data=st.session_state[model_key],
        )

    show_controls = False
    models: Optional[list[dict]] = None
    voices: Optional[list[dict]] = None
    fetch_error = False

    # Only fetch models/voices if API key is present and non-empty
    if st.session_state[model_key]["api_key"]:
        try:
            if (
                "elevenlabs_models" not in st.session_state
                or "elevenlabs_voices" not in st.session_state
            ):
                models_result = call_api(
                    endpoint="action/walker/elevenlabs_tts_action/get_models", json_data={"agent_id": agent_id}
                )
                voices_result = call_api(
                    endpoint="action/walker/elevenlabs_tts_action/get_voices", json_data={"agent_id": agent_id}
                )
                # Defensive checks
                if (
                    not models_result
                    or "error" in models_result
                    or not isinstance(models_result, list)
                    or not voices_result
                    or "error" in voices_result
                    or "voices" not in voices_result
                    or not isinstance(voices_result["voices"], list)
                ):
                    fetch_error = True
                else:
                    st.session_state["elevenlabs_models"] = models_result
                    st.session_state["elevenlabs_voices"] = voices_result["voices"]
                    models = models_result
                    voices = voices_result["voices"]
            else:
                models_candidate = st.session_state.get("elevenlabs_models")
                voices_candidate = st.session_state.get("elevenlabs_voices")
                # Check they're not None and of the expected type
                if isinstance(models_candidate, list):
                    models = models_candidate
                if isinstance(voices_candidate, list):
                    voices = voices_candidate
        except Exception:
            fetch_error = True

        if fetch_error or models is None or voices is None:
            st.error(
                "Failed to fetch models or voices. "
                "Please check your API key and network connection."
            )
        elif not models or not voices:
            st.warning(
                "No models or voices available. Check your API key and/or ElevenLabs account."
            )
        else:
            show_controls = True
    else:
        st.info("Please provide your ElevenLabs API key to proceed.")

    # --- Selection controls (shown only if API key and data present/valid)
    if show_controls:
        # Initialize selection state (model/voice)
        if models and len(models) > 0 and not st.session_state[model_key].get("model"):
            st.session_state[model_key]["model"] = models[0]["model_id"]

        if voices and len(voices) > 0 and not st.session_state[model_key].get("voice"):
            st.session_state[model_key]["voice"] = voices[0]["name"]

        model_info_dict = (
            {
                f"{model['name']} - {model['description']}": model["model_id"]
                for model in models
            }
            if models
            else {}
        )

        voice_info_dict = (
            {f"{voice['name']}": voice["voice_id"] for voice in voices}
            if voices
            else {}
        )

        if model_info_dict:
            selected_model_info = st.selectbox(
                "Text-to-Speech Model:",
                options=list(model_info_dict.keys()),
                index=list(model_info_dict.values()).index(
                    st.session_state[model_key]["model"]
                ),
            )
            st.session_state[model_key]["model"] = model_info_dict[selected_model_info]

        if voice_info_dict:
            selected_voice_info = st.selectbox(
                "Voice:",
                options=list(voice_info_dict.keys()),
                index=list(voice_info_dict.keys()).index(
                    st.session_state[model_key]["voice"]
                ),
            )
            st.session_state[model_key]["voice"] = selected_voice_info

    # --- Always show update action button
    app_update_action(agent_id, action_id)
