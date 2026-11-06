import os
import requests
import csv
from datetime import datetime, timezone
from huggingface_hub import HfApi

print("🚀 STARTING INDEXER V3 (LATEST CODE)")

RPC_URLS = [
    "https://rpc.aex402.com",
    "https://api.mainnet-beta.solana.com"
]
MINT_ADDRESS = "BwUTq7fS6sfUmHDwAiCQZ3asSiPEapW5zDrsbwtapump"
HF_TOKEN = os.environ.get("HF_TOKEN")
REPO_ID = "introspector/solfunmeme"

def get_top_holders():
    payload = {"jsonrpc": "2.0", "id": 1, "method": "getTokenLargestAccounts", "params": [MINT_ADDRESS]}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for url in RPC_URLS:
        print(f"Încercăm RPC-ul: {url}")
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            print(f"Status HTTP: {response.status_code}")
            
            # Afișăm primele 100 de caractere primite, ca să vedem ce ne răspunde serverul
            print(f"Răspuns brut: {response.text[:100]}")
            
            if response.status_code != 200:
                print(f"⚠️ Eroare HTTP {response.status_code} de la {url}.")
                continue
                
            data = response.json()
            if "error" in data:
                print(f"⚠️ Eroare JSON de la {url}: {data['error']}")
                continue
                
            print(f"✅ Succes cu {url}")
            return data["result"]["value"]
            
        except Exception as e:
            print(f"❌ Excepție la {url}: {e}")
            
    raise Exception("Toate RPC-urile au eșuat!")

def save_to_csv(holders):
    timestamp = datetime.now(timezone.utc).isoformat()
    filename = "sfm_top_holders.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp_utc", "wallet_address", "raw_amount", "ui_amount"])
        for h in holders:
            writer.writerow([timestamp, h["address"], h["amount"], h["uiAmount"]])
    return filename

def upload_to_hf(filepath):
    if not HF_TOKEN:
        print("❌ HF_TOKEN lipsește.")
        return
    print("Se urcă direct pe HuggingFace...")
    api = HfApi()
    api.upload_file(
        path_or_fileobj=filepath,
        path_in_repo="csv/sfm_top_holders.csv",
        repo_id=REPO_ID,
        repo_type="dataset",
        token=HF_TOKEN,
        commit_message="Auto-update: Top SFM holders"
    )
    print("✅ Upload complet!")

if __name__ == "__main__":
    holders = get_top_holders()
    filepath = save_to_csv(holders)
    upload_to_hf(filepath)
