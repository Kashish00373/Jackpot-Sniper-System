import multiprocessing, hashlib, base58, requests, time
try:
    from coincurve import PublicKey
    HAS_CC = True
except:
    HAS_CC = False

# --- CONFIGURATION ---
TOKEN = "8711590963:AAH1WxtYCOjxTPIShWzf0zgYjo6gQFB2Uq4"
CHAT_ID = "8619569939"
TARGET_PREFIX = "1PWo3JeB" 
START_HEX = 0x7fffffffffdf00000 

def notify(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

def hunt(start_point, worker_id):
    count = 0
    while True:
        current_hex = hex(start_point + count)[2:].zfill(64)
        if HAS_CC:
            pub = PublicKey.from_valid_secret(bytes.fromhex(current_hex)).format(compressed=True)
        else:
            continue
            
        h = hashlib.new('ripemd160', hashlib.sha256(pub).digest()).digest()
        addr = base58.b58encode_check(b'\x00' + h).decode()
        
        if addr.startswith(TARGET_PREFIX):
            notify(f"🎯 *MATCH FOUND!*\nAddr: `{addr}`\nHEX: `{current_hex}`")
            if addr == "1PWo3JeDH15vMK1KFH4x28zTXyX9XV8aWA":
                notify(f"🚨 *JACKPOT ALERT!* 🚨\nHEX: `{current_hex}`")
                break
        count += 1
        if count % 1000000 == 0 and worker_id == 0:
            notify(f"👷 *Jackpot-Worker-0:* Scanned {count:,} keys...")

if __name__ == "__main__":
    cores = multiprocessing.cpu_count()
    notify(f"🚀 *Jackpot Sniper Online!* \nCores: {cores} | Target: {TARGET_PREFIX}")
    procs = []
    for i in range(cores):
        p = multiprocessing.Process(target=hunt, args=(START_HEX + (i * 0x10000000), i))
        procs.append(p)
        p.start()
    for p in procs: p.join()
