import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal


# =========================================================
# Configuration
# =========================================================

NUM_CUSTOMERS = 100
NUM_DEVICES = 80
NUM_IP_ADDRESSES = 90
NUM_ADDRESSES = 95
NUM_PAYMENT_INSTRUMENTS = 100
NUM_TRANSACTIONS = 1000


# =========================================================
# Helper Functions
# =========================================================

def random_date(days_back: int = 365) -> datetime:
    """Generate a random datetime within the last N days."""
    return datetime.utcnow() - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


def random_amount(
    minimum: float = 100,
    maximum: float = 50000,
) -> Decimal:
    """Generate a random transaction amount."""
    return Decimal(
        str(round(random.uniform(minimum, maximum), 2))
    )


def generate_code(prefix: str, number: int) -> str:
    """Generate a readable unique identifier."""
    return f"{prefix}_{number:06d}"


def generate_hash(prefix: str, number: int) -> str:
    """Generate a deterministic-looking hashed identifier."""
    return f"{prefix}_{uuid.uuid4().hex[:16]}_{number:04d}"


# =========================================================
# Merchants
# =========================================================

def generate_merchants(count: int = 5):
    merchant_names = [
        "Nova Electronics",
        "UrbanCart",
        "TechNest",
        "HomeSphere",
        "StyleHub",
    ]

    merchants = []

    for i in range(count):
        merchants.append(
            {
                "merchant_code": f"MER_{i + 1:04d}",
                "name": merchant_names[i % len(merchant_names)],
                "created_at": random_date(700),
            }
        )

    return merchants


# =========================================================
# Customers
# =========================================================

def generate_customers(
    merchant_ids,
    count: int = NUM_CUSTOMERS,
):
    customers = []

    for i in range(count):
        customers.append(
            {
                "merchant_id": random.choice(merchant_ids),
                "customer_code": f"CUS_{i + 1:06d}",
                "created_at": random_date(500),
            }
        )

    return customers


# =========================================================
# Devices
# =========================================================

def generate_devices(
    merchant_ids,
    count: int = NUM_DEVICES,
):
    devices = []

    for i in range(count):
        devices.append(
            {
                "device_hash": generate_hash("DEV", i + 1),
                "merchant_id": random.choice(merchant_ids),
            }
        )

    return devices


# =========================================================
# IP Addresses
# =========================================================

def generate_ip_addresses(
    merchant_ids,
    count: int = NUM_IP_ADDRESSES,
):
    ip_addresses = []

    for i in range(count):
        ip_addresses.append(
            {
                "ip_hash": generate_hash("IP", i + 1),
                "merchant_id": random.choice(merchant_ids),
            }
        )

    return ip_addresses


# =========================================================
# Addresses
# =========================================================

def generate_addresses(
    merchant_ids,
    count: int = NUM_ADDRESSES,
):
    addresses = []

    for i in range(count):
        addresses.append(
            {
                "address_hash": generate_hash("ADDR", i + 1),
                "merchant_id": random.choice(merchant_ids),
            }
        )

    return addresses


# =========================================================
# Payment Instruments
# =========================================================

def generate_payment_instruments(
    merchant_ids,
    count: int = NUM_PAYMENT_INSTRUMENTS,
):
    instruments = []

    instrument_types = [
        "card",
        "upi",
        "wallet",
        "netbanking",
    ]

    for i in range(count):
        instruments.append(
            {
                "instrument_hash": generate_hash("PAY", i + 1),
                "instrument_type": random.choice(instrument_types),
                "merchant_id": random.choice(merchant_ids),
            }
        )

    return instruments


# =========================================================
# Transactions
# =========================================================

def generate_transactions(
    merchant_ids,
    customer_ids,
    device_ids,
    ip_address_ids,
    address_ids,
    payment_instrument_ids,
    count: int = NUM_TRANSACTIONS,
):
    """
    Generate synthetic transaction records.

    The current version creates realistic transaction behaviour
    and maintains the basic relationships required by LossGraph.
    """

    transactions = []

    for i in range(count):

        status = random.choices(
            ["SUCCESS", "FAILED", "PENDING"],
            weights=[85, 10, 5],
            k=1,
        )[0]

        chargeback = random.random() < 0.04

        refund_status = None

        if status == "SUCCESS":
            refund_status = random.choices(
                ["NONE", "REQUESTED", "REFUNDED"],
                weights=[88, 5, 7],
                k=1,
            )[0]

        transactions.append(
            {
                "transaction_code": f"TXN_{i + 1:06d}",

                "merchant_id": random.choice(
                    merchant_ids
                ),

                "customer_id": random.choice(
                    customer_ids
                ),

                "device_id": random.choice(
                    device_ids
                ),

                "ip_address_id": random.choice(
                    ip_address_ids
                ),

                "address_id": random.choice(
                    address_ids
                ),

                "payment_instrument_id": random.choice(
                    payment_instrument_ids
                ),

                "amount": random_amount(),

                "status": status,

                "refund_status": refund_status,

                "chargeback": chargeback,

                "created_at": random_date(180),
            }
        )

    return transactions