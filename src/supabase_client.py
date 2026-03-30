import os
from supabase import create_client, Client

def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables.")
    return create_client(url, key)

def download_pdf_from_supabase(bucket_name: str, file_path: str, local_save_path: str) -> str:
    """
    Downloads a PDF file from a specified Supabase bucket to the local drive.
    Returns the path to the downloaded local file.
    """
    client = get_supabase_client()
    res = client.storage.from_(bucket_name).download(file_path)
    if not res:
        raise Exception(f"Failed to download {file_path} from bucket {bucket_name}.")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(local_save_path)), exist_ok=True)
    
    with open(local_save_path, "wb") as f:
        f.write(res)
    
    print(f"File downloaded successfully to {local_save_path}")
    return local_save_path
