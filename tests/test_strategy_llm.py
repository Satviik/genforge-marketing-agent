import json

import pytest

from genforge_marketing.profile.models import BusinessProfile, ProductProfile
from genforge_marketing.strategy.llm import (
    OpenAICompatibleStrategyProvider,
    StrategyProviderError,
)
from genforge_marketing.strategy.engine import generate_strategy


class FakeResponse:
    def __init__(self, content: str):
        self.content = content

    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": self.content}}]}


def test_ai_provider_validates_structured_response(monkeypatch) -> None:
    profile = BusinessProfile(
        products=[ProductProfile(name="Custom bookmark")],
        target_audiences=["gift buyers"],
    )
    expected = generate_strategy(profile, 2026, 12).model_dump_json()

    def fake_post(url, **kwargs):
        assert url == "https://api.example.test/v1/chat/completions"
        assert kwargs["headers"]["Authorization"] == "Bearer test-token"
        return FakeResponse(expected)

    monkeypatch.setattr("genforge_marketing.strategy.llm.httpx.post", fake_post)
    provider = OpenAICompatibleStrategyProvider(
        api_key="test-token",
        model="test-model",
        base_url="https://api.example.test/v1",
    )
    result = provider.generate(profile, 2026, 12)
    assert result.business_name == "GenForge"
    assert result.month == 12


def test_ai_provider_rejects_wrong_period(monkeypatch) -> None:
    profile = BusinessProfile(products=[ProductProfile(name="Custom bookmark")])
    wrong_period = generate_strategy(profile, 2027, 1).model_dump_json()
    monkeypatch.setattr(
        "genforge_marketing.strategy.llm.httpx.post",
        lambda *args, **kwargs: FakeResponse(wrong_period),
    )
    provider = OpenAICompatibleStrategyProvider("test-token", "test-model")
    with pytest.raises(StrategyProviderError, match="month/year"):
        provider.generate(profile, 2026, 12)


def test_ai_provider_rejects_invalid_json(monkeypatch) -> None:
    profile = BusinessProfile(products=[ProductProfile(name="Custom bookmark")])
    monkeypatch.setattr(
        "genforge_marketing.strategy.llm.httpx.post",
        lambda *args, **kwargs: FakeResponse("not json"),
    )
    provider = OpenAICompatibleStrategyProvider("test-token", "test-model")
    with pytest.raises(StrategyProviderError, match="invalid structured output"):
        provider.generate(profile, 2026, 12)
