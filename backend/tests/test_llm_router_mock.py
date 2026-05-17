import unittest
from unittest.mock import patch

from llm import router


class TestLLMRouterMock(unittest.TestCase):
    def test_call_llm_uses_groq_by_default(self):
        with patch.object(router, "call_groq", return_value="groq-ok") as groq_mock, patch.object(
            router, "call_gemini", return_value="gemini-ok"
        ) as gemini_mock:
            result = router.call_llm("hello world", system_message="system prompt")

        self.assertEqual(result, "groq-ok")
        groq_mock.assert_called_once()
        gemini_mock.assert_not_called()

    def test_call_llm_falls_back_to_gemini_on_groq_quota_error(self):
        with patch.object(router, "GEMINI_API_KEY", "test-gemini-key"), patch.object(
            router, "call_groq", side_effect=RuntimeError("429 rate limit exceeded")
        ) as groq_mock, patch.object(router, "call_gemini", return_value="gemini-ok") as gemini_mock:
            result = router.call_llm("hello world")

        self.assertEqual(result, "gemini-ok")
        groq_mock.assert_called_once()
        gemini_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
