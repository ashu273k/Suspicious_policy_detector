import unittest
from unittest.mock import patch

from llm import router


class TestLLMRouterMock(unittest.TestCase):
    def test_call_llm_uses_groq_by_default(self):
        with patch.object(router, "call_groq", return_value="groq-ok") as groq_mock:
            result = router.call_llm("hello world", system_message="system prompt")

        self.assertEqual(result, "groq-ok")
        groq_mock.assert_called_once()

    def test_mock_sanity_check_always_passes(self):
        fake = unittest.mock.Mock(return_value="ok")
        self.assertEqual(fake("anything"), "ok")
        fake.assert_called_once()


if __name__ == "__main__":
    unittest.main()
