import os
import asyncio
import python_weather
from ddgs import DDGS
import webbrowser
import urllib.parse
import shutil # Add this at the top
import psutil

def google_search(query):
    try:
        if isinstance(query, dict):
            query = query.get('query') or query.get('value') or str(query)
        print(f"[System] Searching for: {query}")
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(f"{query} March 2026", max_results=2)]
            return " ".join([r['body'] for r in results]) if results else "No info found."
    except: return "Search failed."

async def get_weather(city):
    try:
        async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
            weather = await client.get(city)
            return f"It's {weather.temperature} degrees and {weather.description} in {city}."
    except: return "Weather unavailable."

# NEW FEATURE: System Automation
def close_application(app_name):
    """Closes an application using taskkill."""
    try:
        app_map = {
            "calculator": "CalculatorApp.exe",
            "notepad": "notepad.exe",
            "chrome": "chrome.exe"
        }
        target = app_map.get(app_name.lower(), f"{app_name}.exe")
        # Adding "> NUL 2>&1" makes the SUCCESS/ERROR messages invisible
        result = os.system(f"taskkill /f /im {target} > NUL 2>&1")
        if result == 0:
            return f"I've closed {app_name} for you."
        else:
            return f"No running instance of {app_name} found."
    except Exception as e:
        return f"Error: {e}"

def system_control(command):
    command = command.lower()
    # NEW: Handle Terminal/Friend Exit
    if "close terminal" in command or "stop the program" in command:
        return "exit" # We will handle this in main.py
    # Handle Calculator & Notepad more reliably
    if "calculator" in command:
        if "open" in command or "start" in command:
            os.system("calc.exe")
            return "Opening Calculator."
        if "close" in command or "exit" in command:
            return close_application("calculator")
    if "notepad" in command:
        if "open" in command or "start" in command:
            os.system("notepad.exe")
            return "Opening Notepad."
        if "close" in command or "exit" in command:
            return close_application("notepad")
    return None

def create_project(project_name):
    """Creates a new folder and a python file automatically."""
    try:
        path = f"D:/B.tect/projects/{project_name}"
        if not os.path.exists(path):
            os.makedirs(path)
            with open(f"{path}/main.py", "w") as f:
                f.write("# New Project Created by Friend AI\nprint('Hello World')")
            return f"Project {project_name} created successfully in your D drive."
        else:
            return "That project folder already exists."
    except Exception as e:
        return f"Failed to create project: {e}"

def create_college_project(subject_name, assignment_no):
    """Automatically creates a folder for college work with a template file."""
    try:
        # Base path - change this to your actual projects folder
        base_path = f"D:/B.tect/projects/{subject_name}_Assignment_{assignment_no}"
        
        if not os.path.exists(base_path):
            os.makedirs(base_path)
            # Create a starter python file
            with open(f"{base_path}/solution.py", "w") as f:
                f.write(f'# Assignment {assignment_no} for {subject_name}\n')
                f.write('# Created by Friend AI\n\ndef main():\n    print("System Ready")\n\nif __name__ == "__main__":\n    main()')
            
            # Open the folder in File Explorer automatically
            os.startfile(base_path)
            return f"I've created the folder for {subject_name} and added a solution.py file. Opening it now!"
        else:
            return "That assignment folder already exists, boss."
    except Exception as e:
        return f"Sorry, I couldn't create the folder: {e}"

def delete_project(project_name):
    """Permanently deletes a project folder from the D drive."""
    try:
        # Clean the input if the AI sends a dict
        if isinstance(project_name, dict):
            project_name = project_name.get('project_name') or project_name.get('value')
        path = f"D:/B.tect/projects/{project_name}"
        if os.path.exists(path):
            shutil.rmtree(path) # Deletes the folder and everything inside
            return f"I have permanently deleted the project folder: {project_name}."
        else:
            return f"I couldn't find a folder named {project_name} on your D drive."
    except Exception as e:
        return f"Error while deleting: {e}"

def search_stackoverflow(error_message):
    """Searches Stack Overflow for a specific code error."""
    try:
        print(f"[System] Searching Stack Overflow for: {error_message}")
        # Encode the query for a URL
        query = urllib.parse.quote(f"python {error_message}")
        url = f"https://stackoverflow.com/search?q={query}"
        webbrowser.open(url)
        return f"I've opened Stack Overflow for '{error_message}' in your browser."
    except Exception as e:
        return f"Could not open browser: {e}"

def generate_code_file(filename, task_description):
    """Generates a Python file with logic based on the user's description."""
    try:
        path = f"D:/B.tect/projects/{filename}.py"
        content = f'# Task: {task_description}\n# Generated by Friend AI on March 6, 2026\n\ndef main():\n    print("Starting task: {task_description}")\n\nif __name__ == "__main__":\n    main()'
        with open(path, "w") as f:
            f.write(content)
        os.startfile(path) # Opens the file in your default editor (VS Code/Notepad)
        return f"Created {filename}.py in your projects folder and opened it for you."
    except Exception as e:
        return f"Error creating file: {e}"

def get_quick_news():
    """Fetches the top 3 headlines and cleans the text."""
    try:
        with DDGS() as ddgs:
            # Search for news from the last 24 hours
            results = [r['body'] for r in ddgs.text("india news facts last 24 hours", max_results=5)]
            clean_headlines = []
            for h in results:
                clean = h.split('|')[0].split('-')[0].strip()
                # Only keep factual sentences, filter out opinion or clickbait
                if len(clean) > 15 and any(word in clean.lower() for word in ["announced", "reported", "released", "confirmed", "revealed", "declared", "said", "stated"]):
                    clean_headlines.append(clean)
            if clean_headlines:
                return ". ".join(clean_headlines)
            return "No major headlines right now."
    except:
        return "I couldn't reach the news server."


def get_system_status():
    """Checks CPU, RAM, and Battery levels."""
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()
    status = f"System usage is at {cpu}% CPU and {ram}% RAM."
    if battery:
        status += f" Battery is at {battery.percent}% and {'charging' if battery.power_plugged else 'discharging'}."
    return status

def kill_heavy_processes(threshold=20):
    """Kills processes using more than 'threshold' percent RAM."""
    import psutil
    killed = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            if proc.info['memory_percent'] and proc.info['memory_percent'] > threshold:
                psutil.Process(proc.info['pid']).kill()
                killed.append(f"{proc.info['name']} (PID {proc.info['pid']})")
        except Exception:
            pass
    if killed:
        return f"Killed: {', '.join(killed)}"
    return "No heavy processes found above threshold."