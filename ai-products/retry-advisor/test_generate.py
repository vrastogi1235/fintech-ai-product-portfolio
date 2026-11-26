import unittest
from generate import generate


class GenerateTest(unittest.TestCase):
    def setUp(self):
        self.rows = generate(20_000, seed=1)
        self.failed = [r for r in self.rows if r["status"] == "failed"]

    def test_same_seed_same_data(self):
        self.assertEqual(self.rows, generate(20_000, seed=1))

    def test_only_failures_have_retries(self):
        for r in self.rows:
            has_retry = r["retry_delay_min"] != ""
            self.assertEqual(has_retry, r["status"] == "failed")

    def test_failure_rate_is_plausible(self):
        rate = len(self.failed) / len(self.rows)
        self.assertTrue(0.05 < rate < 0.20, rate)

    def test_hard_declines_rarely_recover(self):
        hard = [r for r in self.failed if r["failure_class"] == "hard_decline"]
        self.assertTrue(hard)
        self.assertLess(sum(r["retry_success"] for r in hard) / len(hard), 0.05)

    def test_waiting_helps_insufficient_funds(self):
        def rate(delay):
            rs = [r["retry_success"] for r in self.failed
                  if r["failure_class"] == "insufficient_funds" and r["retry_delay_min"] == delay]
            return sum(rs) / len(rs)
        self.assertGreater(rate(1440), rate(0))


if __name__ == "__main__":
    unittest.main()
