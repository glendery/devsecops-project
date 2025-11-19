import json
import os
import hashlib
import shutil
from datetime import datetime

BLOCKCHAIN_FILE = "blockchain.json"
BACKUP_DIR = "chain_backup"


def sha256(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()


def backup_chain():
    if not os.path.exists(BLOCKCHAIN_FILE):
        print("[INFO] Tidak ada blockchain.json untuk dibackup.")
        return None

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{BACKUP_DIR}/blockchain_backup_{timestamp}.json"

    shutil.copy(BLOCKCHAIN_FILE, backup_name)
    print(f"[OK] Backup tersimpan: {backup_name}")

    return backup_name


def load_chain():
    if not os.path.exists(BLOCKCHAIN_FILE):
        print("[ERROR] blockchain.json tidak ditemukan.")
        return None

    with open(BLOCKCHAIN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_transaction(tx):
    items = tx.get("items")

    # Jika items bukan string → ubah ke string JSON
    if not isinstance(items, str):
        try:
            items = json.dumps(items, ensure_ascii=False, default=str)
        except:
            items = str(items)

    # Hapus garbage <built-in method ...>
    if "<built-in" in items or "at 0x" in items:
        items = "CORRUPTED_ITEM_REMOVED"

    tx["items"] = items
    return tx


def clean_chain(chain):
    print("\n[INFO] Memulai pembersihan blockchain...\n")

    cleaned = []
    last_hash = None

    for i, block in enumerate(chain):

        # Perbaiki index jika tidak sesuai
        block_index = block.get("index", i + 1)
        if block_index != i + 1:
            print(f"[WARN] Index rusak pada block {block_index}, diperbaiki menjadi {i+1}")
            block["index"] = i + 1

        # Validasi previous hash
        if i > 0:
            expected_prev = sha256(cleaned[i-1])
            if block.get("previous_hash") != expected_prev:
                print(f"[WARN] previous_hash salah pada block #{block['index']}. Memperbaiki.")
                block["previous_hash"] = expected_prev

        # Bersihkan transaksi
        txs = block.get("transactions", [])
        fixed_txs = []

        for tx in txs:
            fixed_txs.append(clean_transaction(tx))

        block["transactions"] = fixed_txs

        cleaned.append(block)

    print("\n[OK] Chain telah dibersihkan.\n")
    return cleaned


def save_chain(chain):
    with open(BLOCKCHAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(chain, f, ensure_ascii=False, indent=2)
    print("[OK] blockchain.json berhasil ditulis ulang.")


def main():
    print("\n===== 🚀 BLOCKCHAIN CLEANER STARTED =====\n")

    chain = load_chain()
    if chain is None:
        return

    backup_chain()

    cleaned = clean_chain(chain)
    save_chain(cleaned)

    print("\n===== ✅ SELESAI — Blockchain sudah bersih =====\n")


if __name__ == "__main__":
    main()
