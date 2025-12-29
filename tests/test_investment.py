import unittest

from banking.accounts.investment import InvestmentAccount
from banking.errors import InvalidOperationError
from banking.types import Owner, Currency


class TestInvestmentAccount(unittest.TestCase):
    def test_portfolio_value_and_projection(self):
        acc = InvestmentAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
            portfolios={"stocks": 200, "bonds": 100},
            expected_yearly_growth=0.1,
        )

        projected = acc.project_yearly_growth(years=1)

        self.assertAlmostEqual(projected, 440.0, places=2)
        info = acc.get_account_info()
        self.assertEqual(info["portfolio_value"], 300.0)
        self.assertEqual(info["expected_yearly_growth"], 0.1)
        self.assertIn("portfolio=", str(acc))

        acc.add_asset("stocks", 50)
        self.assertEqual(acc.portfolio_value, 350.0)

    def test_project_yearly_growth_zero_years(self):
        acc = InvestmentAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
            portfolios={"stocks": 50},
            expected_yearly_growth=0.1,
        )

        projected = acc.project_yearly_growth(years=0)

        self.assertAlmostEqual(projected, 150.0, places=2)

    def test_project_yearly_growth_negative_years(self):
        acc = InvestmentAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
            expected_yearly_growth=0.1,
        )

        with self.assertRaises(InvalidOperationError):
            acc.project_yearly_growth(years=-1)

    def test_invalid_portfolio_asset_type(self):
        acc = InvestmentAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=100,
        )

        with self.assertRaises(InvalidOperationError):
            acc.add_asset("crypto", 100)


if __name__ == "__main__":
    unittest.main()
