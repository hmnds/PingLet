#!/usr/bin/env python3
"""Script to verify X API token and provide troubleshooting steps."""
import httpx
from app.config import settings

def verify_token():
    """Verify X API bearer token."""
    print("=" * 70)
    print("X API Token Verification")
    print("=" * 70)
    
    token = settings.x_api_bearer_token
    
    if not token or token == "your_x_api_bearer_token_here":
        print("\n❌ ERROR: Token not configured!")
        print("\nPlease set X_API_BEARER_TOKEN in your .env file.")
        print("Get your token from: https://developer.x.com/en/portal/dashboard")
        print("\nℹ️  NOTE: The application will run in Mock Mode (using fake data).")
        return
    
    print(f"\n✓ Token found (length: {len(token)} characters)")
    print(f"  Preview: {token[:15]}...{token[-10:]}")
    
    # Test the token
    print("\n" + "-" * 70)
    print("Testing token with X API...")
    print("-" * 70)
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = httpx.get(
            "https://api.twitter.com/2/users/by/username/elonmusk",
            params={"user.fields": "id"},
            headers=headers,
            timeout=30.0
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                print("✅ SUCCESS! Token is valid and working!")
                print(f"   Test user ID: {data['data']['id']}")
            else:
                print("⚠️  Warning: Got 200 but no data in response")
                print(f"   Response: {response.text[:200]}")
        elif response.status_code == 401:
            print("❌ ERROR: 401 Unauthorized")
            print("\nThis means your token is INVALID or EXPIRED.")
            print("\nPossible causes:")
            print("  1. Token was regenerated or revoked")
            print("  2. Token doesn't have 'Read' permissions")
            print("  3. Token is from the wrong app/project")
            print("  4. Token format is incorrect")
            print("\nHow to fix:")
            print("  1. Go to https://developer.x.com/en/portal/dashboard")
            print("  2. Select your app/project")
            print("  3. Go to 'Keys and tokens' tab")
            print("  4. Generate a new 'Bearer Token'")
            print("  5. Make sure your app has 'Read' permissions")
            print("  6. Copy the new token to your .env file")
            print("  7. Restart your backend server")
            
            try:
                error_data = response.json()
                print(f"\nX API Error Details:")
                if "errors" in error_data:
                    for err in error_data["errors"]:
                        print(f"  - {err.get('message', 'Unknown error')} (code: {err.get('code', 'N/A')})")
                else:
                    print(f"  {error_data}")
            except:
                print(f"\nResponse body: {response.text[:300]}")
                
        elif response.status_code == 403:
            print("❌ ERROR: 403 Forbidden")
            print("\nThis means your token doesn't have the required permissions.")
            print("\nHow to fix:")
            print("  1. Go to https://developer.x.com/en/portal/dashboard")
            print("  2. Select your app/project")
            print("  3. Check 'App permissions' - should be 'Read' or higher")
            print("  4. If needed, regenerate your Bearer Token after updating permissions")
            
        elif response.status_code == 429:
            print("⚠️  WARNING: 429 Rate Limit Exceeded")
            print("\nYou've hit the rate limit. Wait a few minutes and try again.")
            
        else:
            print(f"❌ ERROR: Unexpected status code {response.status_code}")
            print(f"\nResponse: {response.text[:500]}")
            
    except httpx.TimeoutException:
        print("❌ ERROR: Request timed out")
        print("Check your internet connection.")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    verify_token()

