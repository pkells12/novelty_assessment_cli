import os
import importlib
import inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_anthropic():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY not found in environment")
        return
    
    # Import and reload anthropic
    import anthropic
    importlib.reload(anthropic)
    
    print(f"Anthropic version: {anthropic.__version__}")
    
    # Check both Client and Anthropic classes
    print("\nClient class signature:")
    if hasattr(anthropic, 'Client'):
        print(inspect.signature(anthropic.Client.__init__))
    else:
        print("anthropic.Client class not found")
    
    print("\nAnthropic class signature:")
    if hasattr(anthropic, 'Anthropic'):
        print(inspect.signature(anthropic.Anthropic.__init__))
    else:
        print("anthropic.Anthropic class not found")
    
    try:
        print("\nTrying to create a Client instance:")
        client = anthropic.Client(api_key=api_key)
        print("✅ Client created successfully")
    except Exception as e:
        print(f"❌ Error creating Client: {e}")
    
    try:
        print("\nTrying to create an Anthropic instance:")
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Anthropic created successfully")
    except Exception as e:
        print(f"❌ Error creating Anthropic: {e}")

if __name__ == "__main__":
    test_anthropic() 