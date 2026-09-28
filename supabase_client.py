# from supabase import create_client
# from dotenv import load_dotenv
# import os

# load_dotenv()

# supabase_url = os.getenv("SUPABASE_URL")
# supabase_key = os.getenv("SUPABASE_KEY")

# supabase = create_client(
#     supabase_url,
#     supabase_key
# )


from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

print("SUPABASE URL:", supabase_url)
print(
    "KEY TYPE:",
    "SECRET KEY" if supabase_key.startswith("sb_secret_") else "OLD/PUBLISHABLE KEY"
)

supabase = create_client(
    supabase_url,
    supabase_key
)