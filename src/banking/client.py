from __future__ import annotations

from dataclasses import dataclass, field

from banking.errors import InvalidOperationError
from banking.types import ClientStatus


@dataclass
class Client:
    full_name: str
    client_id: str
    age: int
    status: ClientStatus = ClientStatus.ACTIVE
    accounts: list[str] = field(default_factory=list)
    contacts: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Validate required fields and age at creation time.
        if not self.full_name or not self.full_name.strip():
            raise InvalidOperationError("Client full_name is required.")
        if not self.client_id or not self.client_id.strip():
            raise InvalidOperationError("Client client_id is required.")
        if self.age < 18:
            raise InvalidOperationError("Client must be at least 18 years old.")
        if not isinstance(self.status, ClientStatus):
            raise InvalidOperationError("Client status must be a ClientStatus.")

    def add_account(self, account_id: str) -> None:
        # Track unique account ids for the client.
        if account_id not in self.accounts:
            self.accounts.append(account_id)

    def remove_account(self, account_id: str) -> None:
        # Remove account id if it exists.
        if account_id in self.accounts:
            self.accounts.remove(account_id)
