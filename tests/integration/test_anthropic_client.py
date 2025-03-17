import os
import sys
import importlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_anthropic_client():
    """Test the Anthropic client."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
        sys.exit(1)
    
    try:
        # Import anthropic fresh
        import anthropic
        # Force reload to ensure we get the latest version
        importlib.reload(anthropic)
        
        print(f"Anthropic library version: {anthropic.__version__}")
        print(f"Anthropic module path: {anthropic.__file__}")
        
        # Create client with minimal arguments
        print("\nCreating client with minimal args...")
        client = anthropic.Anthropic(api_key=api_key)
        
        # Test if the client has the right attributes
        print("\nChecking client attributes:")
        if hasattr(client, "messages"):
            print("✅ Client has messages attribute")
        else:
            print("❌ Client does NOT have messages attribute")
            
        if hasattr(client, "completions"):
            print("✅ Client has completions attribute")
        else:
            print("❌ Client does NOT have completions attribute")
        
        print("\nAttempting simple message call...")
        messages = [{"role": "user", "content": "Hello, how are you?"}]
            
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=messages
        )
        
        print(f"✅ Response: {response.content[0].text[:100]}...")
        print("Test successful!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_anthropic_client() 