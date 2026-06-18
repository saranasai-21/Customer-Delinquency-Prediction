import os
import google.generativeai as genai

# Configure the API Key using environment variables
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(
        api_key=api_key
    )
else:
    print("Warning: Gemini API key not set. Please set the GEMINI_API_KEY environment variable.")

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def recommendation(
        risk,
        probability):

    prompt = f"""

Customer Risk = {risk}

Probability = {probability}

Generate business actions.

"""

    response = model.generate_content(
        prompt
    )

    return response.text