import os
import ollama
import asyncio
import json
import re
from datetime import datetime
from config import WAKE_WORD, MODEL
from engine_voice import speak, listen
from engine_tools import (
    google_search, get_weather, system_control, create_project, 
    create_college_project, search_stackoverflow, generate_code_file, delete_project, get_quick_news
)
from engine_memory import load_memory, update_user_info

def run_friend(user_input):
    # NEW: The "Today's Report" Skill
    if "report" in user_input:
        from engine_tools import get_system_status, get_quick_news
        speak("Compiling today's briefing...")
        status = get_system_status()
        news = get_quick_news()
        report = f"System Status: {status}. Latest Headlines: {news}."
        speak(report)
        return

    # System Health Skill
    if "status report" in user_input or "system status" in user_input:
        from engine_tools import get_system_status
        speak(get_system_status())
        return

    user_input = user_input.lower()
    memory = load_memory()
    now = datetime.now()
    current_date = now.strftime("%B %d, %Y") # e.g., March 07, 2026
    current_time = now.strftime("%I:%M %p")

    # Handle Exit
    if any(word in user_input for word in ["exit", "bye", "stop", "close terminal"]):
        speak(f"Goodbye, {memory['name']}!")
        os._exit(0)

    # 1. Automatic Greeting Filter
    greetings = ["good morning", "hi", "hello", "hey"]
    if any(greet in user_input for greet in greetings):
        news = get_quick_news() # GET LIVE NEWS AUTOMATICALLY
        msg = f"Good morning {memory['name']}. It is {current_time} on {current_date}. Here is what's happening: {news}. How can I help?"
        speak(msg)
        return

    # 2. Handle "Remember my name" commands directly
    if "my name is" in user_input:
        name = user_input.split("is")[-1].strip()
        speak(update_user_info("name", name))
        return

    # 3. System commands
    sys_res = system_control(user_input)
    if sys_res:
        speak(sys_res)
        return

    print("[Thinking...]")
    # 4. Dynamic System Prompt
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                'role': 'system', 
                'content': f"You are JARVIS, a sophisticated AI assistant. Today is {current_date}. "
                           f"The user is {memory['name']}. Be professional and efficient."
            },
            {'role': 'user', 'content': user_input}
        ],
        tools=[
            {'type': 'function', 'function': {
                'name': 'google_search',
                'description': 'General web search for facts, news, and information. Use ONLY for general questions, not programming errors.',
                'parameters': {'type': 'object', 'properties': {'query': {'type': 'string'}}, 'required': ['query']}
            }},
            {'type': 'function', 'function': {'name': 'delete_project', 'description': 'Delete a folder', 'parameters': {'type': 'object', 'properties': {'project_name': {'type': 'string'}}, 'required': ['project_name']}}},
            {'type': 'function', 'function': {'name': 'create_project', 'description': 'Create a project folder', 'parameters': {'type': 'object', 'properties': {'project_name': {'type': 'string'}}, 'required': ['project_name']}}},
            {'type': 'function', 'function': {'name': 'create_college_project', 'description': 'Create college assignment', 'parameters': {'type': 'object', 'properties': {'subject_name': {'type': 'string'}, 'assignment_no': {'type': 'string'}}, 'required': ['subject_name', 'assignment_no']}}},
            {'type': 'function', 'function': {
                'name': 'search_stackoverflow',
                'description': 'Search Stack Overflow ONLY when the user mentions a specific programming error or bug. Do NOT use for general questions.',
                'parameters': {
                    'type': 'object',
                    'properties': {'error_message': {'type': 'string'}},
                    'required': ['error_message']
                }
            }},
            {'type': 'function', 'function': {'name': 'generate_code_file', 'description': 'Create a single python file', 'parameters': {'type': 'object', 'properties': {'filename': {'type': 'string'}, 'task_description': {'type': 'string'}}, 'required': ['filename', 'task_description']}}}
        ]
    )

    message_content = response['message'].get('content', '')
    tool_calls = response['message'].get('tool_calls')

    # --- SAFETY NET: Catch raw JSON even if wrapped in backticks ---
    if not tool_calls:
        try:
            # Find JSON in message_content, even if wrapped in backticks or other chars
            json_match = re.search(r'`?\{.*?\}`?', message_content, re.DOTALL)
            if json_match:
                json_str = json_match.group().strip('`')
                data = json.loads(json_str)
                if data.get("name") == "delete_project" or "delete" in str(data):
                    p_name = data.get("parameters", {}).get("project_name") or data.get("project_name")
                    if p_name:
                        speak(delete_project(p_name))
                        return
                if data.get("name") == "search_stackoverflow":
                    speak(search_stackoverflow(data.get("parameters", {}).get("error_message")))
                    return
                if data.get("name") == "create_project":
                    speak(create_project(data.get("parameters", {}).get("project_name")))
                    return
                if data.get("name") == "create_college_project":
                    speak(create_college_project(data.get("parameters", {}).get("subject_name"), data.get("parameters", {}).get("assignment_no")))
                    return
                if data.get("name") == "generate_code_file":
                    speak(generate_code_file(data.get("parameters", {}).get("filename"), data.get("parameters", {}).get("task_description")))
                    return
                if data.get("name") == "google_search":
                    search_query = data.get("parameters", {}).get("query") or user_input
                    search_data = google_search(search_query)
                    final = ollama.chat(
                        model=MODEL,
                        messages=[
                            {
                                'role': 'system',
                                'content': f"Today is March 7, 2026. Use this search data to answer as Jarvis: {search_data}"
                            },
                            {'role': 'user', 'content': user_input}
                        ]
                    )
                    speak(final['message']['content'])
                    return
        except Exception as e:
            pass

    # --- STANDARD HANDLER ---
    if tool_calls:
        tool = tool_calls[0]
        name = tool['function']['name']
        args = tool['function'].get('arguments', {})

        if name == 'delete_project':
            speak(delete_project(args.get('project_name')))
        elif name == 'google_search':
            data = google_search(args.get('query') or user_input)
            final = ollama.chat(
                model=MODEL,
                messages=[
                    {
                        'role': 'system',
                        'content': f"Today is March 7, 2026. Use this search data to answer as Jarvis: {data}"
                    },
                    {'role': 'user', 'content': user_input}
                ]
            )
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
    speak("Systems online. Jarvis is standing by.") # Updated greeting
    while True:
        voice_input = listen("Say 'Jarvis'") # Changed the visual prompt
        if WAKE_WORD in voice_input:
            speak("At your service.") # More 'Jarvis-like' response
            cmd = listen("How can I help?")
            if cmd: run_friend(cmd)