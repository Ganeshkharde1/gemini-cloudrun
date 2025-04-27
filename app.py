import os
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv # Optional: for loading API key from a .env file

# --- Configuration ---

# Optional: Load environment variables from a .env file in the same directory
# Create a file named .env and add a line like: GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
# load_dotenv()

# Get the API key from the environment variable
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# --- Flask App Setup ---
app = Flask(__name__)

# --- Configure Gemini API ---
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        print("Google Generative AI configured successfully.")
        # Optional: Check if models are available
        # for m in genai.list_models():
        #     print(m.name)
    except Exception as e:
         print(f"Error configuring Google Generative AI: {e}")
         print("Please check your GOOGLE_API_KEY.")
         # The route handler will need to handle this if configuration failed
else:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    print("Please set the GOOGLE_API_KEY environment variable with your Gemini API key.")
    print("Example (Linux/macOS): export GOOGLE_API_KEY='YOUR_KEY'")
    print("Example (Windows): set GOOGLE_API_KEY=YOUR_KEY")


# --- Flask Route Definition ---
@app.route('/generate_response', methods=['POST'])
def generate_response():
    """
    Flask route to accept a user query and return a Gemini response.
    Expects a JSON POST body like: {"query": "your question here"}
    """
    # Check if the API key was set at all
    if not GOOGLE_API_KEY:
        return jsonify({'error': 'Gemini API key is not configured on the server.'}), 500

    # Get the JSON data from the request body
    request_data = request.get_json()

    # Validate input
    if not request_data or 'query' not in request_data:
        return jsonify({'error': 'Invalid request body. Please provide a JSON object with a "query" key.'}), 400

    user_query = request_data['query']

    print(f"Received query: '{user_query}'") # Log the incoming query

    # --- Call Gemini API ---
    try:
        # Choose a model (gemini-pro is good for text generation)
        model = genai.GenerativeModel('gemini-pro')

        # Generate content
        # Note: For more complex interactions (like chat history),
        # you would use model.start_chat()
        response = model.generate_content(user_query)

        # Extract the text response
        # Handle cases where response might not have text (e.g., safety issues)
        if response and response.text:
             gemini_response_text = response.text
             print("Successfully generated Gemini response.")
             # Return the response as JSON
             return jsonify({'response': gemini_response_text}), 200
        else:
             # Handle cases where the API returned an empty or blocked response
             # You might want to inspect response.prompt_feedback or response.candidates
             print(f"Gemini API returned no text or was blocked: {response}")
             return jsonify({'error': 'Gemini API returned no text or was blocked.', 'details': str(response)}), 500


    except Exception as e:
        # Catch any exceptions during the API call (e.g., network issues, invalid key, rate limits)
        print(f"Error calling Gemini API: {e}") # Log the detailed error on the server side
        return jsonify({'error': f'An error occurred while generating response: {e}'}), 500

# --- Run the Flask App ---
if __name__ == '__main__':
    # app.run(debug=True) # Run in debug mode during development
    # Use host='0.0.0.0' to make the server accessible externally (e.g., in Docker or a VM)
    # For local testing, 127.0.0.1 is the default.
    print("Starting Flask server...")
    port = int(os.environ.get('PORT', 8085))  # Use Cloud Run's port if available
    app.run(host='0.0.0.0', port=port, debug=False)
