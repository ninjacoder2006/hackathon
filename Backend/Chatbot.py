from groq import Groq 
from json import load, dump 
import datetime 
from dotenv import dotenv_values 
 



env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GrogAPIKey")

client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
     {"role": "system", "content": System}
]

try:
    with open(r"Data\ChatLog.json", "r") as f:
       messages = load(f) # Load existing messages from the chat log.
except FileNotFoundError: 
    with open(r"Data\ChatLog.json", "w") as f:
       dump([], f)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    
    
    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

# Function to modify the chatbot's response for better formatting
def AnswerModifier(Answer):
    lines = Answer.split('\n') # 1
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer
     
def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    try:
        # Load the existing chat log from the JSON file.
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
        
        # Append the user's query to the messages list.
        messages.append({"role": "user", "content": f"{Query}"})
        # Make a request to the Groq API for a response.
        completion = client.chat.completions.create(
            model="llama3-70b-8192",  
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024, # Limit the maximum tokens in the response.
            temperature=0.7, # Adjust response randomness (higher means more random).
            top_p=1, # Use nucleus sampling to control diversity.
            stream=True, # Enable streaming response.
            stop=None # Allow the model to determine when to stop.
        )
        
        Answer = "" # Initialize an empty string to store the AI's response.

        for chunk in completion:
            if chunk.choices[0].delta.content: # Check if there's
                Answer += chunk.choices[0].delta.content # Append

        Answer = Answer.replace("</s>", "") # Clean up any unwanted text
        # Append the chatbot's response to the messages list
        messages.append({"role": "assistant", "content": Answer})
        
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)
        # Return the formatted response
        return AnswerModifier(Answer)

    except Exception as e:
        # Handle errors by printing the exception and resetting the chat log
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query) # Retry the query after resetting the chat log

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))