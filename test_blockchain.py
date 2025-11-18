import unittest
from app import Blockchain

class TestBlockchain(unittest.TestCase):

    def setUp(self):
        self.blockchain = Blockchain()

    def test_chain_validity(self):
        """Menguji apakah rantai valid saat transaksi normal"""
        self.blockchain.add_transaction("User1", "Kopi", "25000")
        self.blockchain.create_block(1, self.blockchain.hash(self.blockchain.last_block))
        
        self.blockchain.add_transaction("User2", "Buku", "120000")
        self.blockchain.create_block(2, self.blockchain.hash(self.blockchain.last_block))

        # Cek manual integritas
        prev_block = self.blockchain.chain[0]
        for i in range(1, len(self.blockchain.chain)):
            curr_block = self.blockchain.chain[i]
            
            # 1. Cek apakah hash previous cocok
            self.assertEqual(curr_block['previous_hash'], self.blockchain.hash(prev_block))
            prev_block = curr_block

    def test_tampering_detection(self):
        """Menguji apakah sistem mendeteksi jika data dimanipulasi (HACKING TEST)"""
        self.blockchain.add_transaction("User1", "Kopi", "25000")
        self.blockchain.create_block(1, self.blockchain.hash(self.blockchain.last_block))

        # --- SIMULASI SERANGAN ---
        # Hacker mengubah transaksi di blok indeks 1 dari "Kopi" jadi "Mobil"
        self.blockchain.chain[1]['transactions'][0]['product'] = "Mobil Mewah"

        # Cek Integritas lagi - HARUSNYA GAGAL (Hash berubah)
        is_valid = True
        prev_block = self.blockchain.chain[0]
        for i in range(1, len(self.blockchain.chain)):
            curr_block = self.blockchain.chain[i]
            
            # Jika hash blok sebelumnya tidak sama dengan hash yang tercatat di blok sekarang
            if curr_block['previous_hash'] != self.blockchain.hash(prev_block):
                is_valid = False
                break
            prev_block = curr_block
        
        # Kita berharap is_valid menjadi FALSE karena data diubah
        self.assertFalse(is_valid, "Blockchain harus mendeteksi manipulasi data!")

if __name__ == '__main__':
    unittest.main()