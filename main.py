import os
import ollama
import asyncio
import json
import re
from config import WAKE_WORD, MODEL
from engine_voice import speak, listen
from engine_tools import (
    google_search, get_weather, system_control, create_project, 
    create_college_project, search_stackoverflow, generate_code_file, delete_project
)

def run_friend(user_input):
    # Handle Exit
    if any(word in user_input.lower() for word in ["exit", "bye", "stop"]):
        speak("Catch you later!")
        os._exit(0)

    # 1. Check system commands
    sys_res = system_control(user_input)
    if sys_res == "exit": # If system_control says it's time to close the terminal
        speak("Closing the terminal system. Goodbye!")
        os._exit(0)
    elif sys_res:
        speak(sys_res)
        return

    # 2. FAST GREETING CHECK (Add this!)
    greetings = ["good morning", "good afternoon", "hi", "hello", "hey"]
    if user_input.lower().strip() in greetings:
        # Today is March 6, 2026. Let's give it some personality!
        msg = "Good morning! India just beat England last night to reach the T20 World Cup Final, so it's a great morning indeed. How can I help you with your projects today?"
        speak(msg)
        return

    print("[Thinking...]")
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                'role': 'system', 
                'content': (
                    'ACT AS AN AI IN THE YEAR 2026. Today is March 6, 2026. '
                    'Do NOT mention 2023. Do NOT argue about versions. '
                    'If the user says "close terminal", use your logic to exit. '
                    'Keep all answers under 2 sentences.'
                )
            },
            {'role': 'user', 'content': user_input}
        ],
        tools=[
            {'type': 'function', 'function': {'name': 'google_search', 'description': 'Search web', 'parameters': {'type': 'object', 'properties': {'query': {'type': 'string'}}, 'required': ['query']}}},
            {'type': 'function', 'function': {'name': 'delete_project', 'description': 'Delete a folder', 'parameters': {'type': 'object', 'properties': {'project_name': {'type': 'string'}}, 'required': ['project_name']}}},
            {'type': 'function', 'function': {'name': 'create_project', 'description': 'Create a project folder', 'parameters': {'type': 'object', 'properties': {'project_name': {'type': 'string'}}, 'required': ['project_name']}}},
            {'type': 'function', 'function': {'name': 'create_college_project', 'description': 'Create college assignment', 'parameters': {'type': 'object', 'properties': {'subject_name': {'type': 'string'}, 'assignment_no': {'type': 'string'}}, 'required': ['subject_name', 'assignment_no']}}},
            {'type': 'function', 'function': {'name': 'search_stackoverflow', 'description': 'Search for code errors', 'parameters': {'type': 'object', 'properties': {'error_message': {'type': 'string'}}, 'required': ['error_message']}}},
            {'type': 'function', 'function': {'name': 'generate_code_file', 'description': 'Create a single python file', 'parameters': {'type': 'object', 'properties': {'filename': {'type': 'string'}, 'task_description': {'type': 'string'}}, 'required': ['filename', 'task_description']}}}
        ]
    )

    message_content = response['message'].get('content', '')
    tool_calls = response['message'].get('tool_calls')

    # --- SAFETY NET: Catch raw JSON if the model just prints it ---
    if not tool_calls and "{" in message_content:
        try:
            json_match = re.search(r'\{.*\}', message_content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                if data.get("name") == "delete_project" or "delete" in str(data):
                    p_name = data.get("parameters", {}).get("project_name") or data.get("project_name")
                    if p_name:
                        speak(delete_project(p_name))
                        return
        except: pass

    # --- STANDARD HANDLER ---
    if tool_calls:
        tool = tool_calls[0]
        name = tool['function']['name']
        args = tool['function'].get('arguments', {})

        if name == 'delete_project':
            speak(delete_project(args.get('project_name')))
        elif name == 'google_search':
            data = google_search(args.get('query') or user_input)
            final = ollama.chat(model=MODEL, messages=[{'role': 'user', 'content': f"Today is 2026. Data: {data}. Answer: {user_input}"}])
            speak(final['message']['content'])
        elif name == 'create_project':
            speak(create_project(args.get('project_name')))
        elif name == 'create_college_project':
            speak(create_college_project(args.get('subject_name'), args.get('assignment_no')))
        elif name == 'search_stackoverflow':
            speak(search_stackoverflow(args.get('error_message')))
        elif name == 'generate_code_file':
            speak(generate_code_file(args.get('filename'), args.get('task_description')))
    else:
        speak(message_content)

if __name__ == "__main__":
    speak("Modular system online.")
    while True:
        voice_input = listen("Say 'Hey Friend'")
        if WAKE_WORD in voice_input:
            speak("Yes?")
            cmd = listen("How can I help?")
            if cmd: run_friend(cmd)