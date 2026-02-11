"""
Script to discover available models from BRIDGEIT API
"""
from utils import get_llm, get_azure_auth_token
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 80)
print("BRIDGEIT MODEL DISCOVERY")
print("=" * 80)

# Test 1: Check what model is configured
print("\n1. Testing configured model (gpt-4o)...")
try:
    llm = get_llm()
    print(f"   ✓ Model Name: {llm.model_name if hasattr(llm, 'model_name') else llm.model}")
    print(f"   ✓ Type: {type(llm).__name__}")
    print(f"   ✓ Endpoint: {llm.azure_endpoint if hasattr(llm, 'azure_endpoint') else 'N/A'}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Try all models from documentation (Pay-as-you-use tier)
print("\n2. Testing models from documentation...")
test_models = [
    # Current working
    "gpt-4o",
    "gpt-4o-mini",
    # GPT models
    "gpt-4.1",
    "gpt-o4-mini",
    "gpt-o3",
    "gpt-5",
    "gpt-5-2",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-5-chat",
    # Gemini models
    "gemini-2.5-pro-exp",
    "gemini-2.5-flash-preview",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    # Claude models
    "claude-sonnet-4",
    "claude-sonnet-4.5",
    "claude-opus-4.1",
    "claude-opus-4.5",
    "claude-haiku-4.5",
]

working_models = []
for model in test_models:
    try:
        llm = get_llm(model_name=model)
        # Try a simple completion to see if it works
        response = llm.invoke("Say 'OK'")
        print(f"   ✓ {model:20s} - WORKING")
        working_models.append(model)
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"   ✗ {model:20s} - {error_msg}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"\nWorking models ({len(working_models)}):")
for model in working_models:
    print(f"  ✓ {model}")

print("\n" + "=" * 80)
