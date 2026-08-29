'''
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
    count=1000,
):
    """
    Generate realistic synthetic transactions.

    Dataset design:

    1. Mostly normal transactions
       - Customers usually reuse their own resources.
       - A customer normally has one device/IP/address/payment.
       - Small amounts of resource sharing can occur naturally.

    2. Three deliberately injected abuse networks
       - Multiple customers share the same device.
       - Multiple customers share the same IP.
       - Multiple customers share the same address.
       - Multiple customers share the same payment instrument.
       - Transactions have elevated amounts and behavioral risk.

    This creates a meaningful graph:
        Normal transactions -> weak connections
        Abuse networks      -> dense connections
    """

    transactions = []

    now = datetime.utcnow()

    # =====================================================
    # Configuration
    # =====================================================

    NETWORK_COUNT = 3
    NETWORK_SIZE = 10

    abuse_transaction_count = (
        NETWORK_COUNT * NETWORK_SIZE
    )

    normal_count = count - abuse_transaction_count

    # =====================================================
    # Helper: realistic transaction timestamp
    # =====================================================

    def random_transaction_date():
        days_ago = random.randint(0, 180)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)

        return (
            now
            - timedelta(days=days_ago)
            - timedelta(hours=hours_ago)
            - timedelta(minutes=minutes_ago)
        )

    # =====================================================
    # Create a stable resource profile for each customer
    # =====================================================
    #
    # Normal customers should NOT randomly receive a new
    # device/IP/address/payment for every transaction.
    #
    # Instead, each customer gets a primary resource profile.
    #
    # This prevents the entire graph from becoming connected.
    # =====================================================

    customer_profiles = {}

    for index, customer_id in enumerate(customer_ids):
        customer_profiles[customer_id] = {
        "device_id": device_ids[index],

        "ip_address_id": ip_address_ids[index],

        "address_id": address_ids[index],

        "payment_instrument_id": payment_instrument_ids[index],
    }

    # =====================================================
    # Helper: normal transaction
    # =====================================================

    def create_normal_transaction(index):

        customer_id = random.choice(customer_ids)

        profile = customer_profiles[customer_id]

        # -------------------------------------------------
        # Normal transactions mostly use the customer's
        # established resources.
        # -------------------------------------------------

        device_id = profile["device_id"]
        ip_address_id = profile["ip_address_id"]
        address_id = profile["address_id"]
        payment_instrument_id = profile[
            "payment_instrument_id"
        ]

        # -------------------------------------------------
        # Small amount of legitimate resource variation.
        #
        # This prevents the synthetic data from looking
        # completely artificial.
        # -------------------------------------------------

        if random.random() < 0.05:
            device_id = random.choice(device_ids)

        if random.random() < 0.05:
            ip_address_id = random.choice(
                ip_address_ids
            )

        if random.random() < 0.03:
            address_id = random.choice(
                address_ids
            )

        if random.random() < 0.03:
            payment_instrument_id = random.choice(
                payment_instrument_ids
            )

        # -------------------------------------------------
        # Normal amount
        # -------------------------------------------------

        amount = Decimal(
            str(
                round(
                    random.uniform(
                        100,
                        15000,
                    ),
                    2,
                )
            )
        )

        # -------------------------------------------------
        # Normal status
        # -------------------------------------------------

        status = random.choices(
            [
                "SUCCESS",
                "FAILED",
                "PENDING",
            ],
            weights=[
                88,
                8,
                4,
            ],
            k=1,
        )[0]

        # -------------------------------------------------
        # Normal chargeback probability
        # -------------------------------------------------

        chargeback = random.random() < 0.015

        # -------------------------------------------------
        # Normal refund probability
        # -------------------------------------------------

        refund_status = None

        if status == "SUCCESS":

            refund_status = random.choices(
                [
                    "NONE",
                    "REQUESTED",
                    "REFUNDED",
                ],
                weights=[
                    93,
                    3,
                    4,
                ],
                k=1,
            )[0]

        return {
    "transaction_code": f"TXN_{index:06d}",

    "is_abuse": False,

    "merchant_id": merchant_id,
    "customer_id": customer_id,
    "device_id": device_id,
    "ip_address_id": ip_address_id,
    "address_id": address_id,
    "payment_instrument_id": payment_instrument_id,

    "amount": amount,
    "status": status,
    "refund_status": refund_status,
    "chargeback": chargeback,
    "created_at": random_transaction_date(),
}
    # =====================================================
    # 1. Generate normal transactions
    # =====================================================

    for i in range(
        1,
        normal_count + 1,
    ):

        transactions.append(
            create_normal_transaction(i)
        )

    # =====================================================
    # 2. Inject three abuse networks
    # =====================================================
    #
    # Each network contains 10 different customers.
    #
    # Those customers deliberately share:
    #
    #   - device
    #   - IP
    #   - address
    #   - payment instrument
    #
    # This produces a dense graph component.
    # =====================================================

    for network_index in range(
        NETWORK_COUNT
    ):

        # -------------------------------------------------
        # Select customers
        # -------------------------------------------------

        start = (
            network_index
            * NETWORK_SIZE
        )

        customer_group = customer_ids[
            start:start + NETWORK_SIZE
        ]

        if len(customer_group) < NETWORK_SIZE:
            break

        # -------------------------------------------------
        # Shared resources
        # -------------------------------------------------

        shared_device = device_ids[
            network_index
        ]

        shared_ip = ip_address_ids[
            network_index
        ]

        shared_address = address_ids[
            network_index
        ]

        shared_payment = payment_instrument_ids[
            network_index
        ]

        # -------------------------------------------------
        # Assign the network to a merchant
        # -------------------------------------------------

        merchant_id = merchant_ids[
            network_index
            % len(merchant_ids)
        ]

        # -------------------------------------------------
        # Generate abuse transactions
        # -------------------------------------------------

        for transaction_index in range(
            NETWORK_SIZE
        ):

            customer_id = customer_group[
                transaction_index
            ]

            global_index = (
                normal_count
                + (
                    network_index
                    * NETWORK_SIZE
                )
                + transaction_index
                + 1
            )

            # ---------------------------------------------
            # Suspiciously high amounts
            # ---------------------------------------------

            amount = Decimal(
                str(
                    round(
                        random.uniform(
                            15000,
                            75000,
                        ),
                        2,
                    )
                )
            )

            # ---------------------------------------------
            # Abuse transactions mostly succeed
            # ---------------------------------------------

            status = random.choices(
                [
                    "SUCCESS",
                    "FAILED",
                ],
                weights=[
                    95,
                    5,
                ],
                k=1,
            )[0]

            # ---------------------------------------------
            # High chargeback probability
            # ---------------------------------------------

            chargeback = (
                random.random()
                < 0.25
            )

            # ---------------------------------------------
            # High refund probability
            # ---------------------------------------------

            refund_status = None

            if status == "SUCCESS":

                refund_status = random.choices(
                    [
                        "NONE",
                        "REQUESTED",
                        "REFUNDED",
                    ],
                    weights=[
                        45,
                        10,
                        45,
                    ],
                    k=1,
                )[0]

        transactions.append(
    {
        "transaction_code": (
            f"TXN_{global_index:06d}"
        ),

        "is_abuse": True,

        "merchant_id": merchant_id,
        "customer_id": customer_id,

        "device_id": shared_device,
        "ip_address_id": shared_ip,
        "address_id": shared_address,
        "payment_instrument_id": shared_payment,

        "amount": amount,
        "status": status,
        "refund_status": refund_status,
        "chargeback": chargeback,
        "created_at": random_transaction_date(),
    }
)

    # =====================================================
    # 3. Shuffle transactions
    # =====================================================

    random.shuffle(
        transactions
    )

    return transactions
'''
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
    count=1000,
    random_seed=None,
):
    """
    Generate realistic synthetic transactions.

    Dataset design:

    1. Mostly normal transactions
       - Customers usually reuse their own resources.
       - A customer normally has one device/IP/address/payment.
       - Small amounts of resource sharing can occur naturally.

    2. Deliberately injected abuse networks
       - Multiple customers share the same device.
       - Multiple customers share the same IP.
       - Multiple customers share the same address.
       - Multiple customers share the same payment instrument.
       - Transactions have elevated amounts and behavioral risk.

    This creates a meaningful graph:
        Normal transactions -> weak connections
        Abuse networks      -> dense connections

    NOTE ON DATASET SIZE:
    The abuse (minority) class must be large enough for a
    stable train/test split and reliable precision/recall.
    A hardcoded handful of abuse rows (e.g. 30 out of 1000)
    is too small: an 80/20 split can leave as few as 5-6
    abuse rows in the test set, making metrics swing wildly
    between one seeding run and the next. NETWORK_COUNT is
    therefore scaled to a fixed percentage of `count` rather
    than being a fixed constant.
    """

    if random_seed is not None:
        random.seed(random_seed)

    transactions = []

    now = datetime.utcnow()

    # =====================================================
    # Configuration
    # =====================================================

    NETWORK_SIZE = 10

    # Target roughly 8% of the dataset as abuse, in networks
    # of NETWORK_SIZE customers each, with a sane minimum so
    # small datasets still get a usable minority class.
    ABUSE_RATIO = 0.08

    NETWORK_COUNT = max(
        3,
        round(
            (count * ABUSE_RATIO) / NETWORK_SIZE
        ),
    )

    # Never try to build more abuse networks than we have
    # distinct customers to put in them.
    max_networks_by_customers = (
        len(customer_ids) // NETWORK_SIZE
    )

    NETWORK_COUNT = min(
        NETWORK_COUNT,
        max_networks_by_customers,
    )

    abuse_transaction_count = (
        NETWORK_COUNT * NETWORK_SIZE
    )

    normal_count = count - abuse_transaction_count

    # =====================================================
    # Helper: realistic transaction timestamp
    # =====================================================

    def random_transaction_date():
        days_ago = random.randint(0, 180)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)

        return (
            now
            - timedelta(days=days_ago)
            - timedelta(hours=hours_ago)
            - timedelta(minutes=minutes_ago)
        )

    # =====================================================
    # Create a stable resource profile for each customer
    # =====================================================
    #
    # Normal customers should NOT randomly receive a new
    # device/IP/address/payment for every transaction.
    #
    # Instead, each customer gets a primary resource profile.
    #
    # This prevents the entire graph from becoming connected.
    # =====================================================

    customer_profiles = {}

    for index, customer_id in enumerate(customer_ids):
        customer_profiles[customer_id] = {
        "device_id": device_ids[index],

        "ip_address_id": ip_address_ids[index],

        "address_id": address_ids[index],

        "payment_instrument_id": payment_instrument_ids[index],
    }

    # =====================================================
    # Helper: normal transaction
    # =====================================================

    def create_normal_transaction(index):

        merchant_id = random.choice(merchant_ids)

        customer_id = random.choice(customer_ids)

        profile = customer_profiles[customer_id]

        # -------------------------------------------------
        # Normal transactions mostly use the customer's
        # established resources.
        # -------------------------------------------------

        device_id = profile["device_id"]
        ip_address_id = profile["ip_address_id"]
        address_id = profile["address_id"]
        payment_instrument_id = profile[
            "payment_instrument_id"
        ]

        # -------------------------------------------------
        # Small amount of legitimate resource variation.
        #
        # This prevents the synthetic data from looking
        # completely artificial.
        # -------------------------------------------------

        if random.random() < 0.05:
            device_id = random.choice(device_ids)

        if random.random() < 0.05:
            ip_address_id = random.choice(
                ip_address_ids
            )

        if random.random() < 0.03:
            address_id = random.choice(
                address_ids
            )

        if random.random() < 0.03:
            payment_instrument_id = random.choice(
                payment_instrument_ids
            )

        # -------------------------------------------------
        # Normal amount
        # -------------------------------------------------

        amount = Decimal(
            str(
                round(
                    random.uniform(
                        100,
                        15000,
                    ),
                    2,
                )
            )
        )

        # -------------------------------------------------
        # Normal status
        # -------------------------------------------------

        status = random.choices(
            [
                "SUCCESS",
                "FAILED",
                "PENDING",
            ],
            weights=[
                88,
                8,
                4,
            ],
            k=1,
        )[0]

        # -------------------------------------------------
        # Normal chargeback probability
        # -------------------------------------------------

        chargeback = random.random() < 0.015

        # -------------------------------------------------
        # Normal refund probability
        # -------------------------------------------------

        refund_status = None

        if status == "SUCCESS":

            refund_status = random.choices(
                [
                    "NONE",
                    "REQUESTED",
                    "REFUNDED",
                ],
                weights=[
                    93,
                    3,
                    4,
                ],
                k=1,
            )[0]

        return {
    "transaction_code": f"TXN_{index:06d}",

    "is_abuse": False,

    "merchant_id": merchant_id,
    "customer_id": customer_id,
    "device_id": device_id,
    "ip_address_id": ip_address_id,
    "address_id": address_id,
    "payment_instrument_id": payment_instrument_id,

    "amount": amount,
    "status": status,
    "refund_status": refund_status,
    "chargeback": chargeback,
    "created_at": random_transaction_date(),
}
    # =====================================================
    # 1. Generate normal transactions
    # =====================================================

    for i in range(
        1,
        normal_count + 1,
    ):

        transactions.append(
            create_normal_transaction(i)
        )

    # =====================================================
    # 2. Inject three abuse networks
    # =====================================================
    #
    # Each network contains 10 different customers.
    #
    # Those customers deliberately share:
    #
    #   - device
    #   - IP
    #   - address
    #   - payment instrument
    #
    # This produces a dense graph component.
    # =====================================================

    for network_index in range(
        NETWORK_COUNT
    ):

        # -------------------------------------------------
        # Select customers
        # -------------------------------------------------

        start = (
            network_index
            * NETWORK_SIZE
        )

        customer_group = customer_ids[
            start:start + NETWORK_SIZE
        ]

        if len(customer_group) < NETWORK_SIZE:
            break

        # -------------------------------------------------
        # Shared resources
        # -------------------------------------------------

        shared_device = device_ids[
            network_index
        ]

        shared_ip = ip_address_ids[
            network_index
        ]

        shared_address = address_ids[
            network_index
        ]

        shared_payment = payment_instrument_ids[
            network_index
        ]

        # -------------------------------------------------
        # Assign the network to a merchant
        # -------------------------------------------------

        merchant_id = merchant_ids[
            network_index
            % len(merchant_ids)
        ]

        # -------------------------------------------------
        # Generate abuse transactions
        # -------------------------------------------------

        for transaction_index in range(
            NETWORK_SIZE
        ):

            customer_id = customer_group[
                transaction_index
            ]

            global_index = (
                normal_count
                + (
                    network_index
                    * NETWORK_SIZE
                )
                + transaction_index
                + 1
            )

            # ---------------------------------------------
            # Suspiciously high amounts
            # ---------------------------------------------

            amount = Decimal(
                str(
                    round(
                        random.uniform(
                            15000,
                            75000,
                        ),
                        2,
                    )
                )
            )

            # ---------------------------------------------
            # Abuse transactions mostly succeed
            # ---------------------------------------------

            status = random.choices(
                [
                    "SUCCESS",
                    "FAILED",
                ],
                weights=[
                    95,
                    5,
                ],
                k=1,
            )[0]

            # ---------------------------------------------
            # High chargeback probability
            # ---------------------------------------------

            chargeback = (
                random.random()
                < 0.25
            )

            # ---------------------------------------------
            # High refund probability
            # ---------------------------------------------

            refund_status = None

            if status == "SUCCESS":

                refund_status = random.choices(
                    [
                        "NONE",
                        "REQUESTED",
                        "REFUNDED",
                    ],
                    weights=[
                        45,
                        10,
                        45,
                    ],
                    k=1,
                )[0]

            transactions.append(
                {
                    "transaction_code": (
                        f"TXN_{global_index:06d}"
                    ),

                    "is_abuse": True,

                    "merchant_id": merchant_id,
                    "customer_id": customer_id,

                    "device_id": shared_device,
                    "ip_address_id": shared_ip,
                    "address_id": shared_address,
                    "payment_instrument_id": shared_payment,

                    "amount": amount,
                    "status": status,
                    "refund_status": refund_status,
                    "chargeback": chargeback,
                    "created_at": random_transaction_date(),
                }
            )

    # =====================================================
    # 3. Shuffle transactions
    # =====================================================

    random.shuffle(
        transactions
    )

    return transactions