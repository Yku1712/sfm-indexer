import os
import requests
import csv
from datetime import datetime, timezone
from huggingface_hub import HfApi

RPC_URL = "https://rpc.aex402.com"
MINT_ADDRESS = "BwUTq7fS6sfUmHDwAiCQZ3asSiPEapW5zDrsbwtapump"
HF_TOKEN = os.environ.get("HF_TOKEN")
REPO_ID = "introspector/solfunmeme"

def get_top_holders():
    payload = {"jsonrpc": "2.0", "id": 1, "method": "getTokenLargestAccounts", "params": [MINT_ADDRESS]}
    response = requests.post(RPC_URL, json=payload).json()
    if "error" in response:
        raise Exception(f"RPC Error: {response['error']}")
    return response["result"]["value"]

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
        commit_message="Auto-update: Top SFM holders (10-min cron)"
        # Am scos create_pr=True, facem push direct
    )
    print("✅ Upload complet! Datele sunt live pe HuggingFace.")

if __name__ == "__main__":
    holders = get_top_holders()
    filepath = save_to_csv(holders)
    upload_to_hf(filepath)
