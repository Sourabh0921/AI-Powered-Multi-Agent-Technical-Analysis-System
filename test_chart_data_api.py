"""
Quick test script to verify chart data is returned by the API
Run this to check if backend is providing price_data and indicator_data
"""

import requests
import json

# Configuration
API_URL = "http://localhost:8000"
TEST_TICKER = "HDFCBANK.NS"  # Change to any valid ticker

def test_chart_data():
    print("=" * 60)
    print("CHART DATA API TEST")
    print("=" * 60)
    
    # First, login to get token (if auth is required)
    print("\n1. Testing authentication...")
    try:
        login_response = requests.post(
            f"{API_URL}/api/v1/auth/login",
            data={
                "username": "test_user",  # Change to your username
                "password": "test123"     # Change to your password
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print("✅ Authentication successful")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print("❌ Authentication failed, trying without auth...")
            headers = {}
    except Exception as e:
        print(f"⚠️ Auth endpoint not available: {e}")
        print("Trying without authentication...")
        headers = {}
    
    # Test AI analysis endpoint
    print(f"\n2. Testing AI analysis for {TEST_TICKER}...")
    try:
        analysis_response = requests.post(
            f"{API_URL}/api/v1/ai/analyze",
            json={
                "ticker": TEST_TICKER,
                "query": f"analyze {TEST_TICKER}",
                "risk_tolerance": "moderate",
                "period": "6mo"
            },
            headers=headers
        )
        
        if analysis_response.status_code == 200:
            data = analysis_response.json()
            print("✅ API request successful")
            
            # Check if result exists
            if "result" in data:
                result = data["result"]
                print("\n3. Checking chart data fields...")
                
                # Check price_data
                if "price_data" in result:
                    price_data = result["price_data"]
                    print(f"✅ price_data found: {len(price_data)} data points")
                    if len(price_data) > 0:
                        print(f"   First item: {json.dumps(price_data[0], indent=2)}")
                        
                        # Validate structure
                        first_item = price_data[0]
                        required_fields = ["date", "open", "high", "low", "close", "volume"]
                        missing = [f for f in required_fields if f not in first_item]
                        if missing:
                            print(f"❌ Missing fields: {missing}")
                        else:
                            print("✅ All required fields present (date, open, high, low, close, volume)")
                    else:
                        print("❌ price_data is empty!")
                else:
                    print("❌ price_data NOT FOUND in response!")
                
                # Check indicator_data
                if "indicator_data" in result:
                    indicator_data = result["indicator_data"]
                    print(f"\n✅ indicator_data found: {len(indicator_data)} data points")
                    if len(indicator_data) > 0:
                        print(f"   First item: {json.dumps(indicator_data[0], indent=2)}")
                        
                        # Check for key indicators
                        first_item = indicator_data[0]
                        indicators = ["rsi", "macd", "sma_20", "sma_50"]
                        present = [i for i in indicators if i in first_item]
                        print(f"   Indicators present: {', '.join(present)}")
                    else:
                        print("❌ indicator_data is empty!")
                else:
                    print("❌ indicator_data NOT FOUND in response!")
                
                # Check other fields
                print("\n4. Checking other fields...")
                other_fields = ["ticker", "analysis", "latest_price", "rsi", "macd", "signal"]
                for field in other_fields:
                    if field in result:
                        print(f"✅ {field}: {result[field] if field != 'analysis' else 'Present (truncated)'}")
                    else:
                        print(f"❌ {field}: NOT FOUND")
                
                # Summary
                print("\n" + "=" * 60)
                print("SUMMARY")
                print("=" * 60)
                
                has_price = "price_data" in result and len(result.get("price_data", [])) > 0
                has_indicator = "indicator_data" in result and len(result.get("indicator_data", [])) > 0
                
                if has_price and has_indicator:
                    print("✅ SUCCESS: Chart data is being returned by API")
                    print("   → If charts still don't show, the issue is in the frontend")
                    print("   → Check browser console for errors")
                    print("   → Verify StockCharts component is receiving the data")
                elif not has_price and not has_indicator:
                    print("❌ PROBLEM: No chart data in API response")
                    print("   → Backend needs to return price_data and indicator_data")
                    print("   → Check ta_agent/src/api/v1/endpoints/ai.py")
                    print("   → Look for chart_data preparation code around line 120")
                elif not has_price:
                    print("⚠️ PARTIAL: Missing price_data")
                    print("   → Backend needs to include price_data in response")
                else:
                    print("⚠️ PARTIAL: Missing indicator_data")
                    print("   → Backend needs to include indicator_data in response")
                
            else:
                print("❌ No 'result' field in response")
                print(f"Response keys: {list(data.keys())}")
        else:
            print(f"❌ API request failed: {analysis_response.status_code}")
            print(f"Response: {analysis_response.text}")
    
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chart_data()
