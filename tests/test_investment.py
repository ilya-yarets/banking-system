import unittest
from decimal import Decimal

from banking.accounts.investment import InvestmentAccount
from banking.errors import InvalidOperationError
from banking.types import Owner, Currency


class TestInvestmentAccount(unittest.TestCase):
    def test_portfolio_value_and_projection(self):
        acc = InvestmentAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
            portfolios={"stocks": Decimal("200.00"), "bonds": Decimal("100.00")},
            expected_yearly_growth=Decimal("0.1"),
        )

        projected = acc.project_yearly_growth(years=1)

        self.assertEqual(projected, Decimal("440.00"))
        info = acc.get_account_info()
        self.assertEqual(info["portfolio_value"], Decimal("300.00"))
        self.assertEqual(info["expected_yearly_growth"], Decimal("0.1"))
        self.assertIn("portfolio=", str(acc))

        acc.add_asset("stocks", Decimal("50.00"))
        self.assertEqual(acc.portfolio_value, Decimal("350.00"))

    def test_project_yearly_growth_zero_years(self):
        acc = InvestmentAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
            portfolios={"stocks": Decimal("50.00")},
            expected_yearly_growth=Decimal("0.1"),
        )

        projected = acc.project_yearly_growth(years=0)

        self.assertEqual(projected, Decimal("150.00"))

    def test_project_yearly_growth_negative_years(self):
        acc = InvestmentAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
            expected_yearly_growth=Decimal("0.1"),
        )

        with self.assertRaises(InvalidOperationError):
            acc.project_yearly_growth(years=-1)

    def test_invalid_portfolio_asset_type(self):
        acc = InvestmentAccount(
            owner=Owner("Ilya"),
            currency=Currency.USD,
            balance=Decimal("100.00"),
        )

        with self.assertRaises(InvalidOperationError):
            acc.add_asset("crypto", Decimal("100.00"))


if __name__ == "__main__":
    unittest.main()
