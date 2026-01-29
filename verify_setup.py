import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.universal_ai import UniversalAI

def main():
    print("--- Local AI Campaign Assistant Verification ---")
    
    try:
        ai = UniversalAI(provider_name="ollama")
        
        print(f"Checking provider: {ai.provider_name}...")
        if not ai.provider.is_available():
            print(f"❌ Error: {ai.provider_name} is not available. Is the server running?")
            return

        print(f"✅ {ai.provider_name} is UP!")
        
        models = ai.provider.list_models()
        print(f"Available models: {', '.join(models) if models else 'None'}")
        
        test_prompt = "Hello! Briefly state who you are and if you're ready to help with fundraising campaigns."
        print(f"\nSending test prompt: '{test_prompt}'")
        
        response = ai.generate(test_prompt)
        
        print("\n--- AI Response ---")
        print(response.content)
        print("--------------------")
        print(f"Model: {response.model}")
        print(f"Time: {response.generation_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")

if __name__ == "__main__":
    main()
