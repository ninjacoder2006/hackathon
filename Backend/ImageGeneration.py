import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# Debug: Print the API key to verify it's loaded correctly
print(f"API Key: {get_key('.env', 'HuggingFaceAPIKey')}")

# Function to open and display images based on a given prompt.
def open_images(prompt):
    folder_path = r"Data"  # Folder where the images are stored
    prompt = prompt.replace(" ", "_")  # Replace spaces in prompt
    
    # Generate the filenames for the images
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        
        if os.path.exists(image_path):
            try:
                # Try to open and display the image
                img = Image.open(image_path)
                print(f"Opening image: {image_path}")
                img.show()
                sleep(1)  # Pause for 1 second before showing the next image
            except IOError:
                print(f"Unable to open {image_path}")
        else:
            print(f"File not found: {image_path}")

# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"  # Updated model
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Async function to send a query to the Hugging Face API
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        print(f"API request failed with status code: {response.status_code}")
        print(f"Response: {response.text}")  # Debug: Print the response text
        return None

async def generate_images(prompt: str):
    tasks = []

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
        await asyncio.sleep(1)  # Add a delay to avoid rate limiting
    
    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            image_path = fr"Data\{prompt.replace(' ', '_')}{i + 1}.jpg"
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            print(f"Image saved: {image_path}")
        else:
            print(f"Failed to generate image {i + 1}")

def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))  # Run the async image generation function
    open_images(prompt)  # Open the generated images

# Main loop to monitor for image generation requests
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()
        
        Prompt, Status = Data.split(",")
        
        if Status.strip() == "True":
            print("Generating Images ...")
            GenerateImages(prompt=Prompt.strip())
        
            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False, False")
            break  # Exit the loop after processing the request
        else:
            sleep(1)  # Wait for 1 second before checking again
    except Exception as e:
        print(f"An error occurred: {e}")