import webbrowser
from config import Settings
# Your client_id and redirect_uri
client_id = Settings().client_id
redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"

# Construct the authorization URL
auth_url = f"https://api.fyers.in/api/v3/app/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"

# Open the authorization URL in a web browser
webbrowser.open(auth_url)