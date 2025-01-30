# main.py
import os
from util.gemini_api import ask_gemini


def main():
    # Get the API key from the environment variable
    api_key = os.getenv("GEMINI_API")
    if not api_key:
        print("Error: GEMINI_API environment variable not set.")
        return

    # Question to ask the Gemini API
    question = "Say something in japanese and than the same thing in english"

    # Get the response from Gemini API
    response = ask_gemini(question, api_key)

    # Print the response
    if "error" in response:
        print("Error:", response["error"])
    else:
        print("Response from Gemini:")
        print(response)


if __name__ == "__main__":
    main()
