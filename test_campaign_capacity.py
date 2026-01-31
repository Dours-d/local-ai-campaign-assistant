import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.universal_ai import UniversalAI

def main():
    print("--- Campaign Management Capacity Test ---")
    
    ai = UniversalAI(provider_name="ollama")
    
    # Sample Campaign Data
    campaign_vars = {
        "project_title": "Clean Water for Gaza",
        "goal_amount": "€5000",
        "context": "Water infrastructure was damaged. We need to install 5 solar-powered desalination units to provide potable water to 10,000 residents."
    }
    
    print(f"Testing model: {ai.provider.default_model}")
    print(f"Goal: {campaign_vars['project_title']}\n")

    try:
        response, validation = ai.run_validated_prompt(
            "prompts/campaign/create_campaign.md",
            campaign_vars
        )
        
        print("--- Generated Content ---")
        print(response.content)
        print("\n--- Efficiency Marker (Step 3 Assessment) ---")
        print(f"Primary Marker Passed: {'✅ YES' if validation.passed else '❌ NO'}")
        print(f"Quality Score: {validation.score * 100:.1f}%")
        
        if validation.suggestions:
            print("\nDetailed breakdown:")
            for rule, status in validation.criteria_results.items():
                print(f"- {rule}: {'✅' if status else '❌'}")
            
            print("\nIssues/Suggestions:")
            for s in validation.suggestions:
                print(f"- {s}")
                
        print(f"\nModel: {response.model}")
        print(f"Time: {response.generation_time:.2f}s")

    except Exception as e:
        print(f"❌ Test Failed: {str(e)}")

if __name__ == "__main__":
    main()
