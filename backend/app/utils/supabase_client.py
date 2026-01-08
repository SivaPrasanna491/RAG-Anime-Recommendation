import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


url: str = os.getenv("SUPABASE_API_URL")
key: str = os.getenv("SUPABASE_API_KEY")
client: Client = create_client(supabase_url=url, supabase_key=key)