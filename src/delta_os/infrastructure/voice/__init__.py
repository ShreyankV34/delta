"""Voice infrastructure extension points for Phase-1 text/voice adapters."""

from delta_os.infrastructure.voice.push_to_talk_listener import PushToTalkEvent, PushToTalkListener
from delta_os.infrastructure.voice.speech_to_text_adapter import NullSpeechToTextAdapter, SpeechToTextAdapter
from delta_os.infrastructure.voice.text_to_speech_adapter import LocalTextToSpeechStub, TextToSpeechAdapter

__all__ = [
    "LocalTextToSpeechStub",
    "NullSpeechToTextAdapter",
    "PushToTalkEvent",
    "PushToTalkListener",
    "SpeechToTextAdapter",
    "TextToSpeechAdapter",
]
