from __future__ import annotations

from delta_os.infrastructure.voice import (
    LocalTextToSpeechStub,
    NullSpeechToTextAdapter,
    PushToTalkListener,
)


def test_null_stt_adapter_returns_empty_transcript() -> None:
    transcript = NullSpeechToTextAdapter().transcribe(b"dummy-audio")

    assert transcript == ""


def test_local_tts_stub_tracks_mute_and_last_text() -> None:
    tts = LocalTextToSpeechStub()

    assert tts.speak("hello") == "spoken"
    assert tts.last_text == "hello"
    tts.set_muted(True)
    assert tts.speak("world") == "muted"
    assert tts.last_text == "world"


def test_push_to_talk_listener_returns_idle_event() -> None:
    event = PushToTalkListener().poll()

    assert event.state == "idle"
    assert event.transcript == ""
