'''
import sys
from pathlib import Path

# Allow imports from the backend directory
sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete

from app.db.session import SessionLocal
from app.models.merchant import Merchant
from app.models.customer import Customer
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.models.address import Address
from app.models.payment_instrument import PaymentInstrument
from app.models.transaction import Transaction
from app.models.abuse_cluster import AbuseCluster
from app.models.abuse_cluster_member import AbuseClusterMember

from app.utils.synthetic_data import (
    generate_merchants,
    generate_customers,
    generate_devices,
    generate_ip_addresses,
    generate_addresses,
    generate_payment_instruments,
    generate_transactions,
)


def clear_database(db):
    """
    Delete existing records from the tables that this seed
    script currently manages.

    Child tables must be deleted before parent tables because
    of foreign-key constraints.
    """

    print("Clearing existing seed data...")

    db.execute(delete(AbuseClusterMember))
    db.execute(delete(AbuseCluster))
    db.execute(delete(Transaction))
    db.execute(delete(PaymentInstrument))
    db.execute(delete(Address))
    db.execute(delete(IPAddress))
    db.execute(delete(Device))
    db.execute(delete(Customer))
    db.execute(delete(Merchant))

    db.commit()

    print("Existing seed data cleared.")


def seed_database():
    db = SessionLocal()

    try:
        # -------------------------------------------------
        # 1. Clear existing data
        # -------------------------------------------------

        clear_database(db)

        # -------------------------------------------------
        # 2. Create merchants
        # -------------------------------------------------

        merchant_data = generate_merchants(5)

        merchants = [
            Merchant(**data)
            for data in merchant_data
        ]

        db.add_all(merchants)
        db.flush()

        merchant_ids = [
            merchant.id
            for merchant in merchants
        ]

        print(f"Created {len(merchants)} merchants.")

        # -------------------------------------------------
        # 3. Create customers
        # -------------------------------------------------

        customer_data = generate_customers(
            merchant_ids,
            count=100,
        )

        customers = [
            Customer(**data)
            for data in customer_data
        ]

        db.add_all(customers)
        db.flush()

        print(f"Created {len(customers)} customers.")

        # -------------------------------------------------
        # 4. Create devices
        # -------------------------------------------------

        device_data = generate_devices(
            merchant_ids,
            count=150,
        )

        devices = [
            Device(**data)
            for data in device_data
        ]

        db.add_all(devices)
        db.flush()

        print(f"Created {len(devices)} devices.")

        # -------------------------------------------------
        # 5. Create IP addresses
        # -------------------------------------------------

        ip_data = generate_ip_addresses(
            merchant_ids,
            count=150,
        )

        ip_addresses = [
            IPAddress(**data)
            for data in ip_data
        ]

        db.add_all(ip_addresses)
        db.flush()

        print(f"Created {len(ip_addresses)} IP addresses.")

        # -------------------------------------------------
        # 6. Create addresses
        # -------------------------------------------------

        address_data = generate_addresses(
            merchant_ids,
            count=150,
        )

        addresses = [
            Address(**data)
            for data in address_data
        ]

        db.add_all(addresses)
        db.flush()

        print(f"Created {len(addresses)} addresses.")

        # -------------------------------------------------
        # 7. Create payment instruments
        # -------------------------------------------------

        payment_data = generate_payment_instruments(
            merchant_ids,
            count=150,
        )

        payment_instruments = [
            PaymentInstrument(**data)
            for data in payment_data
        ]

        db.add_all(payment_instruments)
        db.flush()

        print(
            f"Created {len(payment_instruments)} "
            "payment instruments."
        )
                # -------------------------------------------------
        # 8. Create transactions
        # -------------------------------------------------

        customer_ids = [
            customer.id
            for customer in customers
        ]

        device_ids = [
            device.id
            for device in devices
        ]

        ip_address_ids = [
            ip.id
            for ip in ip_addresses
        ]

        address_ids = [
            address.id
            for address in addresses
        ]

        payment_instrument_ids = [
            payment.id
            for payment in payment_instruments
        ]

        transaction_data = generate_transactions(
            merchant_ids=merchant_ids,
            customer_ids=customer_ids,
            device_ids=device_ids,
            ip_address_ids=ip_address_ids,
            address_ids=address_ids,
            payment_instrument_ids=payment_instrument_ids,
            count=1000,
        )

        transactions = [
            Transaction(**data)
            for data in transaction_data
        ]

        db.add_all(transactions)
        db.flush()

        print(
            f"Created {len(transactions)} transactions."
        )

        # -------------------------------------------------
        # Commit
        # -------------------------------------------------

        db.commit()

        print()
        print("========================================")
        print("Base database seeding successful!")
        print("========================================")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
'''
import sys
from pathlib import Path

# Allow imports from the backend directory
sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete

from app.db.session import SessionLocal
from app.models.merchant import Merchant
from app.models.customer import Customer
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.models.address import Address
from app.models.payment_instrument import PaymentInstrument
from app.models.transaction import Transaction
from app.models.abuse_cluster import AbuseCluster
from app.models.abuse_cluster_member import AbuseClusterMember

from app.utils.synthetic_data import (
    generate_merchants,
    generate_customers,
    generate_devices,
    generate_ip_addresses,
    generate_addresses,
    generate_payment_instruments,
    generate_transactions,
)


def clear_database(db):
    """
    Delete existing records from the tables that this seed
    script currently manages.

    Child tables must be deleted before parent tables because
    of foreign-key constraints.
    """

    print("Clearing existing seed data...")

    db.execute(delete(AbuseClusterMember))
    db.execute(delete(AbuseCluster))
    db.execute(delete(Transaction))
    db.execute(delete(PaymentInstrument))
    db.execute(delete(Address))
    db.execute(delete(IPAddress))
    db.execute(delete(Device))
    db.execute(delete(Customer))
    db.execute(delete(Merchant))

    db.commit()

    print("Existing seed data cleared.")


def seed_database():
    db = SessionLocal()

    try:
        # -------------------------------------------------
        # 1. Clear existing data
        # -------------------------------------------------

        clear_database(db)

        # -------------------------------------------------
        # 2. Create merchants
        # -------------------------------------------------

        merchant_data = generate_merchants(5)

        merchants = [
            Merchant(**data)
            for data in merchant_data
        ]

        db.add_all(merchants)
        db.flush()

        merchant_ids = [
            merchant.id
            for merchant in merchants
        ]

        print(f"Created {len(merchants)} merchants.")

        # -------------------------------------------------
        # 3. Create customers
        # -------------------------------------------------

        customer_data = generate_customers(
            merchant_ids,
            count=100,
        )

        customers = [
            Customer(**data)
            for data in customer_data
        ]

        db.add_all(customers)
        db.flush()

        print(f"Created {len(customers)} customers.")

        # -------------------------------------------------
        # 4. Create devices
        # -------------------------------------------------

        device_data = generate_devices(
            merchant_ids,
            count=150,
        )

        devices = [
            Device(**data)
            for data in device_data
        ]

        db.add_all(devices)
        db.flush()

        print(f"Created {len(devices)} devices.")

        # -------------------------------------------------
        # 5. Create IP addresses
        # -------------------------------------------------

        ip_data = generate_ip_addresses(
            merchant_ids,
            count=150,
        )

        ip_addresses = [
            IPAddress(**data)
            for data in ip_data
        ]

        db.add_all(ip_addresses)
        db.flush()

        print(f"Created {len(ip_addresses)} IP addresses.")

        # -------------------------------------------------
        # 6. Create addresses
        # -------------------------------------------------

        address_data = generate_addresses(
            merchant_ids,
            count=150,
        )

        addresses = [
            Address(**data)
            for data in address_data
        ]

        db.add_all(addresses)
        db.flush()

        print(f"Created {len(addresses)} addresses.")

        # -------------------------------------------------
        # 7. Create payment instruments
        # -------------------------------------------------

        payment_data = generate_payment_instruments(
            merchant_ids,
            count=150,
        )

        payment_instruments = [
            PaymentInstrument(**data)
            for data in payment_data
        ]

        db.add_all(payment_instruments)
        db.flush()

        print(
            f"Created {len(payment_instruments)} "
            "payment instruments."
        )
                # -------------------------------------------------
        # 8. Create transactions
        # -------------------------------------------------

        customer_ids = [
            customer.id
            for customer in customers
        ]

        device_ids = [
            device.id
            for device in devices
        ]

        ip_address_ids = [
            ip.id
            for ip in ip_addresses
        ]

        address_ids = [
            address.id
            for address in addresses
        ]

        payment_instrument_ids = [
            payment.id
            for payment in payment_instruments
        ]

        transaction_data = generate_transactions(
            merchant_ids=merchant_ids,
            customer_ids=customer_ids,
            device_ids=device_ids,
            ip_address_ids=ip_address_ids,
            address_ids=address_ids,
            payment_instrument_ids=payment_instrument_ids,
            count=1000,
            random_seed=42,
        )

        transactions = [
            Transaction(**data)
            for data in transaction_data
        ]

        db.add_all(transactions)
        db.flush()

        print(
            f"Created {len(transactions)} transactions."
        )

        # -------------------------------------------------
        # Commit
        # -------------------------------------------------

        db.commit()

        print()
        print("========================================")
        print("Base database seeding successful!")
        print("========================================")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()