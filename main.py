from gemini_api import GeminiAPI


def main():
    # Initialize the Gemini API client
    base_url = "https://api.gemini.example.com"  # Replace with the actual API base URL

    try:
        gemini_client = GeminiAPI(base_url)
    except ValueError as e:
        print(e)
        return

    # Ask a question
    question = input("Enter your question: ")
    response = gemini_client.ask_question(question)

    # Print the response
    print("Gemini's Response:", response)


if __name__ == "__main__":
    main()
