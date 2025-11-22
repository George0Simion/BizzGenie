# test.py

import ai_wrapper



system_prompt = "You are a helpful assistant."
user_prompt = "Tell me about the sky"
reply = ai_wrapper.generate_reply(system_prompt, user_prompt)
print("AI Reply:", reply)
