"""
Test script to verify that different models are actually being used
"""
from utils import get_llm
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("TESTING PAID TIER MODELS - VERIFICATION")
print("=" * 80)

# Test models with a simple prompt that asks them to identify themselves
test_prompt = "In one sentence, tell me your model name and who created you."

models_to_test = [
    "gpt-5",
    "gpt-5-2", 
    "claude-sonnet-4",
    "gemini-2.5-pro",
    "gpt-4o"
]

print("\nTesting models with identity verification prompt...")
print(f"Prompt: '{test_prompt}'\n")

for model in models_to_test:
    print("-" * 80)
    print(f"Testing: {model}")
    print("-" * 80)
    
    try:
        llm = get_llm(model_name=model)
        response = llm.invoke(test_prompt)
        
        # Extract content
        content = response.content if hasattr(response, 'content') else str(response)
        
        print(f"✓ SUCCESS")
        print(f"Response: {content}")
        print()
        
    except Exception as e:
        print(f"✗ FAILED")
        print(f"Error: {str(e)[:200]}")
        print()

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("\nIf the responses show different model identities, the models are working!")
print("If they all say the same thing, there might be a routing issue.")
