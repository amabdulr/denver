"""
Test script to validate which models work with the Analysis & Summary workflow
Tests both SelfQueryRetriever and simple search pathways
"""

import os
from dotenv import load_dotenv
import streamlit as st

# Load environment
load_dotenv()

# Import necessary functions
from app_functions import run_agent
from vector_store_manager import initialize_vector_store

def test_model(model_name, product_name, question, rca_content, vector_store):
    """
    Test a single model with the analysis workflow
    
    Returns:
        dict: {
            'model': model_name,
            'status': 'success' or 'error',
            'error_message': str (if error),
            'output_length': int (if success)
        }
    """
    print(f"\n{'='*60}")
    print(f"Testing model: {model_name}")
    print(f"{'='*60}")
    
    # Mock session state
    class MockSessionState:
        def __init__(self):
            self.selected_model = model_name
            self.vector_store = vector_store
            self.vector_store_initialized = True
        
        def get(self, key, default=None):
            return getattr(self, key, default)
    
    # Replace st.session_state temporarily
    original_session_state = st.session_state
    st.session_state = MockSessionState()
    
    try:
        # Run the agent
        result = run_agent(product_name, question, rca_content)
        
        # Extract output
        output = result.get('output', str(result))
        output_length = len(output)
        
        print(f"✅ SUCCESS - Generated {output_length} characters")
        
        # Restore session state
        st.session_state = original_session_state
        
        return {
            'model': model_name,
            'status': 'success',
            'error_message': None,
            'output_length': output_length
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERROR - {error_msg}")
        
        # Restore session state
        st.session_state = original_session_state
        
        return {
            'model': model_name,
            'status': 'error',
            'error_message': error_msg,
            'output_length': 0
        }

def main():
    """Run tests on all models"""
    
    print("\n" + "="*80)
    print("MODEL COMPATIBILITY TEST - Analysis & Summary Workflow")
    print("="*80)
    
    # Initialize vector store
    print("\n🔄 Initializing vector store...")
    try:
        vector_store = initialize_vector_store()
        print("✅ Vector store loaded successfully")
    except Exception as e:
        print(f"❌ Failed to initialize vector store: {e}")
        return
    
    # Test data
    product_name = "Cisco 9800"
    question = "Analyze this bug and determine where it should be documented"
    rca_content = """
    Bug: CSCwp12345
    Component: ewlc-docs
    Description: Login security configuration blocks SSH connections after failed login attempts.
    The self-defense ACL (sl_def_acl) remains active even after the block period expires,
    preventing legitimate SSH access. This occurs after HA switchover events.
    
    Root Cause: The login block mechanism applies an ACL to VTY lines but does not
    properly remove it after the quiet period expires, especially during HA events.
    
    Workaround: Access via console and manually remove the sl_def_acl from configuration.
    """
    
    # Models to test
    models_to_test = [
        "gpt-4",
        "gpt-4.1",
        "gpt-4o",
        "gpt-5",
        "gpt-5-2",
        "gpt-5-chat",
        "gpt-5-mini",
        "gpt-4o-mini",
        "gpt-5-nano",
        "claude-sonnet-4",
        "gemini-2.5-pro",
        "gemini-2.5-flash"
    ]
    
    # Run tests
    results = []
    for model in models_to_test:
        result = test_model(model, product_name, question, rca_content, vector_store)
        results.append(result)
    
    # Summary report
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    successful_models = [r for r in results if r['status'] == 'success']
    failed_models = [r for r in results if r['status'] == 'error']
    
    print(f"\n✅ SUCCESSFUL MODELS ({len(successful_models)}/{len(models_to_test)}):")
    for result in successful_models:
        print(f"  • {result['model']:<25} ({result['output_length']} chars)")
    
    print(f"\n❌ FAILED MODELS ({len(failed_models)}/{len(models_to_test)}):")
    for result in failed_models:
        error_preview = result['error_message'][:100] + "..." if len(result['error_message']) > 100 else result['error_message']
        print(f"  • {result['model']:<25} {error_preview}")
    
    # Categorize errors
    print("\n📊 ERROR CATEGORIES:")
    function_calling_errors = [r for r in failed_models if 'function' in r['error_message'].lower()]
    other_errors = [r for r in failed_models if 'function' not in r['error_message'].lower()]
    
    if function_calling_errors:
        print(f"\n  Function calling errors ({len(function_calling_errors)}):")
        for r in function_calling_errors:
            print(f"    - {r['model']}")
    
    if other_errors:
        print(f"\n  Other errors ({len(other_errors)}):")
        for r in other_errors:
            print(f"    - {r['model']}: {r['error_message'][:50]}...")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if successful_models:
        print(f"  • Mark these as ✅ (full features): {', '.join([r['model'] for r in successful_models])}")
    if function_calling_errors:
        print(f"  • Mark these as ⚠️ (fallback mode): {', '.join([r['model'] for r in function_calling_errors])}")
    if other_errors:
        print(f"  • These need investigation: {', '.join([r['model'] for r in other_errors])}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
