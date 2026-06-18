"""
Backfill merchant_clean for existing transactions using the current
PayeeNormalizer.

Why this exists: PayeeNormalizer improves over time (bug fixes, new
canonical mappings), but those improvements only affect transactions
normalised during a future sync. Existing rows keep whatever
merchant_clean value was computed at the time they were first synced,
even after the underlying bug is fixed. This script re-runs the current
normalizer against merchant_raw for every transaction and updates
merchant_clean where the result has changed.

Usage:
    # Dry run (default) — shows what would change, writes nothing
    docker compose exec backend python -m scripts.backfill_merchant_clean

    # Actually commit the changes
    docker compose exec backend python -m scripts.backfill_merchant_clean --commit

    # Limit the dry-run sample output (default 20)
    docker compose exec backend python -m scripts.backfill_merchant_clean --sample 50
"""
import argparse
import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.transaction import Transaction
from app.services.payee_normalizer import PayeeNormalizer


async def backfill(commit: bool, sample_size: int) -> None:
    normalizer = PayeeNormalizer()

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Transaction))
        transactions = result.scalars().all()

        changed = []
        for tx in transactions:
            new_clean = normalizer.normalize(tx.merchant_raw)
            if new_clean != tx.merchant_clean:
                changed.append((tx, tx.merchant_clean, new_clean))

        print(f"Scanned {len(transactions)} transactions.")
        print(f"{len(changed)} would change.\n")

        if changed:
            print(f"Sample of changes (showing up to {sample_size}):")
            for tx, old_val, new_val in changed[:sample_size]:
                print(f"  {tx.merchant_raw!r}")
                print(f"    {old_val!r} -> {new_val!r}")

        if not commit:
            print("\nDry run only — no changes written. Re-run with --commit to apply.")
            return

        for tx, _old_val, new_val in changed:
            tx.merchant_clean = new_val

        await session.commit()
        print(f"\nCommitted. Updated {len(changed)} transaction(s).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-apply PayeeNormalizer to existing transactions."
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Actually write changes. Without this flag, runs as a dry run.",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=20,
        help="Number of example changes to print (default: 20).",
    )
    args = parser.parse_args()

    asyncio.run(backfill(commit=args.commit, sample_size=args.sample))


if __name__ == "__main__":
    main()
