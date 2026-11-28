import unittest

from analysis import best_delay, failure_rate_by_rail, recovery_table


def row(rail="card", status="failed", cls="technical", delay=0, ok=0):
    return {"rail": rail, "status": status, "failure_class": cls,
            "retry_delay_min": delay, "retry_success": ok}


class AnalysisTest(unittest.TestCase):
    def test_failure_rate_by_rail(self):
        rows = [row("card"), row("card", "success"), row("upi", "success")]
        self.assertEqual(failure_rate_by_rail(rows), {"card": 0.5, "upi": 0.0})

    def test_recovery_table_counts_and_rates(self):
        rows = [row(delay=60, ok=1), row(delay=60, ok=0), row(delay=0, ok=0),
                row(status="success", cls="", delay="", ok="")]
        table = recovery_table(rows)
        self.assertEqual(table[("technical", 60)], (2, 0.5))
        self.assertEqual(table[("technical", 0)], (1, 0.0))
        self.assertEqual(len(table), 2)

    def test_best_delay_picks_highest_rate_for_that_class_only(self):
        table = {("a", 0): (10, 0.1), ("a", 60): (10, 0.4), ("b", 0): (10, 0.9)}
        self.assertEqual(best_delay(table, "a"), 60)


if __name__ == "__main__":
    unittest.main()
