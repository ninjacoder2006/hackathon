import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values


env_vars = dotenv_values(".env")
AssistanceVoice = env_vars.get("AssistanceVoice")



async def TextToAudioFile(text):
    file_path = r"Data\Speech.mp3"

    if os.path.exists(file_path):
        os.remove(file_path)

    communicate = edge_tts.Communicate(text, AssistanceVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(r'Data\Speech.mp3')


def TTS(text, func=lambda r=None: True):
    try:
        asyncio.run(TextToAudioFile(text))

        pygame.mixer.init()
        pygame.mixer.music.load(r"Data\Speech.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if not func():
                break
            pygame.time.Clock().tick(10)

        return True

    except Exception as e:
        print(f"Error in TTS: {e}")

    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")


def TextToSpeech(text, func=lambda r=None: True):
    data = str(text).split(".")
    
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(data) > 4 and len(text) >= 250:
        TTS(" ".join(data[:2]) + " . " + random.choice(responses), func)
    else:
        TTS(text, func)


if __name__ == "__main__":
    while True:
        TextToSpeech(input("Enter the text: "))