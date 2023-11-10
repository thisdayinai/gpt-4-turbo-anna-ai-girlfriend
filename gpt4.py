from openai import OpenAI
import json

def openai_direct_completion(messages, system_instruction, functions, max_tokens_to_sample=500, temperature=0.2, stop_sequences=["User:"], stream=False):
    client = OpenAI()

    try:
        resp = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages = messages,
            temperature=temperature,
            max_tokens=max_tokens_to_sample,
            frequency_penalty=0.02,
            stream=stream,
            stop=stop_sequences,
            functions=functions
        )
    except Exception as e:
        print("Error calling OpenAI", e)
        return {
            'error': f"An error occurred running. This is temporary and you can try again.",
            'suggestions': ["Try again"],
        }

    # If not streaming we can count the usage now
    if not stream:
        # Extract the completion
        try:
            completion = None
            print(resp)
            for choice in resp.choices:
                if choice.finish_reason == "function_call":
                    # It wants us to call
                    fn = choice.message.function_call
                    print("It wants us to call", fn)
                    if fn.name == "ask_image_question":
                        # parse the fn.arguments as json
                        args = json.loads(fn.arguments)
                        completion = ask_image_question(args['question'])
                    if fn.name == "make_image":
                        # parse the fn.arguments as json
                        args = json.loads(fn.arguments)
                        completion = make_image(args['prompt'])
                        print(completion)
                else:
                    completion = choice.message.content
            return completion
        except Exception as e:
            print("Error extracting completion", e)
            return {
                'error': f"An error occurred running. This is temporary and you can try again.",
                'suggestions': ["Try again"],
            }

    return resp

def make_image(prompt):
    client = OpenAI()
    resp = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    print(resp.data[0].url, resp.data[0].revised_prompt)
    return resp.data[0].url, resp.data[0].revised_prompt


def ask_image_question(question):
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": """https://oaidalleapiprodscus.blob.core.windows.net/private/org-XPp4IBH7Dug3zGHHg3eKcftV/user-355fPQtULxcDr5r7kr3ha2ZL/img-9dW2Ps5lhVt9ylQGUTGNBhCa.png?st=2023-11-09T20%3A52%3A30Z&se=2023-11-09T22%3A52%3A30Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-11-09T19%3A54%3A40Z&ske=2023-11-10T19%3A54%3A40Z&sks=b&skv=2021-08-06&sig=LocNxuaXWYBPKnxniFtJKj9ky1s7lMudVU8u%2BobJHRE%3D""",
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    print(response.choices[0])