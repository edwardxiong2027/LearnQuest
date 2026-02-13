#!/usr/bin/env python3
"""
LearnQuest Cross-Platform Launcher
Replaces setup.sh/start.sh/stop.sh with a single script for Mac, Windows, and Linux.

Usage:
    python launch.py setup   # First-time setup
    python launch.py start   # Start LearnQuest
    python launch.py stop    # Stop LearnQuest
    python launch.py wizard  # Interactive setup wizard
    python launch.py         # Defaults to 'start'
"""

import os
import sys
import json
import platform
import subprocess
import socket
import signal
import time
import webbrowser
import shutil

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(SCRIPT_DIR, 'app')
MODELS_DIR = os.path.join(SCRIPT_DIR, 'ollama_models')
VENV_DIR = os.path.join(APP_DIR, 'venv')
PID_DIR = os.path.join(SCRIPT_DIR, '.pids')
DB_PATH = os.path.join(APP_DIR, 'database', 'learnquest.db')
SCHEMA_PATH = os.path.join(APP_DIR, 'database', 'schema.sql')
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')

SYSTEM = platform.system()  # 'Darwin', 'Windows', 'Linux'
IS_WINDOWS = SYSTEM == 'Windows'
IS_MAC = SYSTEM == 'Darwin'
IS_LINUX = SYSTEM == 'Linux'
IS_CHROMEBOOK = IS_LINUX and os.path.exists('/dev/.cros_milestone')


# ============================================================
# ANSI COLOR HELPERS
# ============================================================
def _enable_ansi():
    """Enable ANSI escape codes on Windows 10+."""
    if IS_WINDOWS:
        os.system('')  # enables ANSI on Win10+

_enable_ansi()

def _supports_color():
    """Check if terminal supports ANSI colors."""
    if IS_WINDOWS:
        return os.environ.get('ANSICON') or os.environ.get('WT_SESSION') or 'TERM' in os.environ
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

USE_COLOR = _supports_color()

def c(text, code):
    """Apply ANSI color code to text."""
    if not USE_COLOR:
        return text
    return f'\033[{code}m{text}\033[0m'

def bold(text):    return c(text, '1')
def blue(text):    return c(text, '34')
def green(text):   return c(text, '32')
def yellow(text):  return c(text, '33')
def red(text):     return c(text, '31')
def cyan(text):    return c(text, '36')
def magenta(text): return c(text, '35')
def dim(text):     return c(text, '2')


# ============================================================
# CONFIG MANAGEMENT
# ============================================================
DEFAULT_CONFIG = {
    'model': 'llama3.2:3b',
    'port': 5001,
    'setup_completed': False,
}

def load_config():
    """Load config from config.json, with defaults."""
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                saved = json.load(f)
            config.update(saved)
        except (json.JSONDecodeError, IOError):
            pass
    return config

def save_config(config):
    """Save config to config.json."""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

config = load_config()
PORT = int(os.environ.get('LEARNQUEST_PORT', config.get('port', 5001)))


# ============================================================
# MODEL OPTIONS
# ============================================================
MODEL_OPTIONS = [
    {
        'id': 'llama3.2:3b',
        'name': 'Llama 3.2 3B',
        'params': '3B',
        'disk': '~2.0 GB',
        'ram': '8 GB+',
        'best_for': 'K-8 (Recommended, included on USB)',
    },
    {
        'id': 'phi3:medium',
        'name': 'Phi-3 Medium',
        'params': '14B',
        'disk': '~7.9 GB',
        'ram': '16 GB+',
        'best_for': 'K-12 (Best Quality, included on USB)',
    },
    {
        'id': 'phi3',
        'name': 'Phi-3 Mini',
        'params': '3.8B',
        'disk': '~2.3 GB',
        'ram': '8 GB+',
        'best_for': 'K-12 (requires download)',
    },
    {
        'id': 'llama3.2:1b',
        'name': 'Llama 3.2 1B',
        'params': '1B',
        'disk': '~1.3 GB',
        'ram': '4 GB+',
        'best_for': 'K-5 (Basic/Low-spec, requires download)',
    },
]


# ============================================================
# UTILITY FUNCTIONS
# ============================================================
def python_executable():
    """Get the venv python path."""
    if IS_WINDOWS:
        return os.path.join(VENV_DIR, 'Scripts', 'python.exe')
    return os.path.join(VENV_DIR, 'bin', 'python')


def pip_executable():
    """Get the venv pip path."""
    if IS_WINDOWS:
        return os.path.join(VENV_DIR, 'Scripts', 'pip.exe')
    return os.path.join(VENV_DIR, 'bin', 'pip')


def port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def read_pid(name):
    """Read a PID from the PID file."""
    pid_file = os.path.join(PID_DIR, f'{name}.pid')
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, IOError):
            pass
    return None


def write_pid(name, pid):
    """Write a PID to a file."""
    os.makedirs(PID_DIR, exist_ok=True)
    with open(os.path.join(PID_DIR, f'{name}.pid'), 'w') as f:
        f.write(str(pid))


def remove_pid(name):
    """Remove a PID file."""
    pid_file = os.path.join(PID_DIR, f'{name}.pid')
    if os.path.exists(pid_file):
        os.remove(pid_file)


def kill_pid(pid):
    """Kill a process by PID."""
    try:
        if IS_WINDOWS:
            subprocess.run(['taskkill', '/PID', str(pid), '/F'],
                         capture_output=True, timeout=10)
        else:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        return True
    except (ProcessLookupError, PermissionError, subprocess.TimeoutExpired):
        return False


def process_alive(pid):
    """Check if a process is still running."""
    if pid is None:
        return False
    try:
        if IS_WINDOWS:
            result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'],
                                  capture_output=True, text=True, timeout=5)
            return str(pid) in result.stdout
        else:
            os.kill(pid, 0)
            return True
    except (ProcessLookupError, PermissionError, subprocess.TimeoutExpired):
        return False


def find_ollama():
    """Find the ollama executable."""
    return shutil.which('ollama')


def ollama_running():
    """Check if Ollama server is already running."""
    return port_in_use(11434)


def get_disk_free_gb(path):
    """Get free disk space in GB for the given path."""
    try:
        usage = shutil.disk_usage(path)
        return usage.free / (1024 ** 3)
    except Exception:
        return -1


def detect_os_display():
    """Return a human-friendly OS name."""
    if IS_MAC:
        ver = platform.mac_ver()[0]
        return f'macOS {ver}' if ver else 'macOS'
    if IS_CHROMEBOOK:
        return 'ChromeOS (Linux)'
    if IS_LINUX:
        try:
            import distro
            return distro.name(pretty=True)
        except ImportError:
            pass
        return 'Linux'
    if IS_WINDOWS:
        return f'Windows {platform.version()}'
    return SYSTEM


# ============================================================
# WIZARD
# ============================================================
def cmd_wizard():
    """Interactive setup wizard with model selection and system checks."""
    print()
    print(blue('=' * 56))
    print(blue('|') + bold('    LearnQuest Setup Wizard'.center(54)) + blue('|'))
    print(blue('|') + '    Learn Without Limits'.center(54) + blue('|'))
    print(blue('=' * 56))
    print()

    # Step 1: OS Detection
    os_name = detect_os_display()
    arch = platform.machine()
    print(f'  {green(">")} {bold("System:")} {os_name} ({arch})')
    print()

    if IS_CHROMEBOOK:
        print(yellow('  Note: Chromebook detected. Make sure Linux (Crostini) is enabled.'))
        print()

    # Step 2: Python check
    py_ver = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
    if sys.version_info >= (3, 8):
        print(f'  {green(">")} {bold("Python:")} {green(py_ver)} {green("OK")}')
    else:
        print(f'  {red(">")} {bold("Python:")} {red(py_ver)} {red("(3.8+ required)")}')
        print()
        print(red('  Python 3.8 or later is required.'))
        if IS_MAC:
            print('  Install: brew install python3')
        elif IS_LINUX:
            print('  Install: sudo apt install python3')
        elif IS_WINDOWS:
            print('  Install from: https://python.org/downloads/')
        return False
    print()

    # Step 3: Ollama check
    ollama_path = find_ollama()
    if ollama_path:
        print(f'  {green(">")} {bold("Ollama:")} {green("Installed")} at {dim(ollama_path)}')
    else:
        print(f'  {yellow(">")} {bold("Ollama:")} {yellow("Not found")}')
        print()
        print('  Ollama is required for the AI tutor. Install it:')
        if IS_MAC:
            print(f'    {cyan("brew install ollama")}  or  {cyan("https://ollama.com/download")}')
        elif IS_LINUX or IS_CHROMEBOOK:
            print(f'    {cyan("curl -fsSL https://ollama.com/install.sh | sh")}')
        elif IS_WINDOWS:
            print(f'    {cyan("https://ollama.com/download/windows")}')
        print()
        resp = input('  Install Ollama now? [Y/n] ').strip().lower()
        if resp in ('', 'y', 'yes'):
            if IS_MAC or IS_LINUX:
                print('  Installing Ollama...')
                try:
                    subprocess.run(['sh', '-c', 'curl -fsSL https://ollama.com/install.sh | sh'],
                                 check=True, timeout=300)
                    print(f'  {green("Ollama installed successfully!")}')
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    print(red('  Failed to install Ollama. Please install manually.'))
                    return False
            elif IS_WINDOWS:
                print('  Please download from https://ollama.com/download/windows')
                print('  After installing, run this wizard again.')
                return False
        else:
            print(yellow('  Skipping Ollama install. AI tutor will not work without it.'))
    print()

    # Step 4: Model selection
    print(f'  {bold("Choose an AI model:")}')
    print()
    # Table header
    hdr = f'  {"#":>3}  {"Model":<16} {"Params":<8} {"Disk":<10} {"RAM":<8} {"Best For"}'
    print(dim(hdr))
    print(dim('  ' + '-' * 70))
    for i, m in enumerate(MODEL_OPTIONS, 1):
        rec = ' (Recommended)' if i == 1 else ''
        line = f'  {i:>3}  {m["name"]:<16} {m["params"]:<8} {m["disk"]:<10} {m["ram"]:<8} {m["best_for"]}{rec}'
        if i == 1:
            print(green(line))
        else:
            print(line)
    print()

    while True:
        choice = input(f'  Select model [1-{len(MODEL_OPTIONS)}] (default: 1): ').strip()
        if choice == '':
            choice = '1'
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(MODEL_OPTIONS):
                selected_model = MODEL_OPTIONS[idx]
                break
        except ValueError:
            pass
        print(red(f'  Please enter a number 1-{len(MODEL_OPTIONS)}'))

    print(f'  {green(">")} Selected: {bold(selected_model["name"])} ({selected_model["id"]})')
    print()

    # Step 5: Disk space check
    free_gb = get_disk_free_gb(SCRIPT_DIR)
    if free_gb > 0:
        print(f'  {green(">")} {bold("Disk space:")} {free_gb:.1f} GB free')
        disk_str = selected_model['disk'].replace('~', '').replace(' GB', '')
        try:
            needed = float(disk_str)
            if free_gb < needed + 1:
                print(yellow(f'  Warning: Model needs {selected_model["disk"]}. You may not have enough space.'))
                resp = input('  Continue anyway? [y/N] ').strip().lower()
                if resp not in ('y', 'yes'):
                    print('  Aborting. Free up disk space and try again.')
                    return False
        except ValueError:
            pass
    print()

    # Step 6: Port selection
    port = config.get('port', 5001)
    port_input = input(f'  Server port (default: {port}): ').strip()
    if port_input:
        try:
            port = int(port_input)
        except ValueError:
            print(yellow(f'  Invalid port, using {port}'))
    print()

    # Step 7: Confirmation
    print(blue('  ' + '-' * 40))
    print(f'  {bold("Summary:")}')
    print(f'    OS:    {os_name}')
    print(f'    Model: {selected_model["name"]} ({selected_model["id"]})')
    print(f'    Port:  {port}')
    print(blue('  ' + '-' * 40))
    print()
    resp = input('  Proceed with setup? [Y/n] ').strip().lower()
    if resp not in ('', 'y', 'yes'):
        print('  Setup cancelled.')
        return False
    print()

    # Save config
    config['model'] = selected_model['id']
    config['port'] = port
    config['setup_completed'] = True
    save_config(config)

    # Run setup with the selected model
    return _run_setup(selected_model['id'])


def _run_setup(model_id):
    """Run the actual setup steps (venv, deps, model pull, DB init)."""
    print(bold('  Running setup...'))
    print()

    # Step 1: Check/install Ollama
    print(f'  {cyan("[1/5]")} Checking Ollama...')
    ollama_path = find_ollama()
    if ollama_path:
        print(f'    {green("OK")} Ollama found at: {ollama_path}')
    else:
        if IS_MAC or IS_LINUX:
            print('    Installing Ollama...')
            try:
                subprocess.run(['sh', '-c', 'curl -fsSL https://ollama.com/install.sh | sh'],
                             check=True, timeout=300)
                print(f'    {green("OK")} Ollama installed.')
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                print(yellow('    WARNING: Could not install Ollama. AI features will not work.'))
        elif IS_WINDOWS:
            print(yellow('    Ollama not found. Install from https://ollama.com/download/windows'))
    print()

    # Step 2: Pull model
    print(f'  {cyan("[2/5]")} Pulling model: {bold(model_id)} (this may take a while)...')
    os.makedirs(MODELS_DIR, exist_ok=True)
    env = os.environ.copy()
    env['OLLAMA_MODELS'] = MODELS_DIR

    ollama_was_running = ollama_running()
    ollama_proc = None
    if not ollama_was_running:
        ollama_cmd = find_ollama() or 'ollama'
        try:
            ollama_proc = subprocess.Popen([ollama_cmd, 'serve'],
                                          env=env,
                                          stdout=subprocess.DEVNULL,
                                          stderr=subprocess.DEVNULL)
            time.sleep(3)
        except FileNotFoundError:
            print(yellow('    Cannot start Ollama. Skipping model pull.'))
            ollama_proc = None

    if find_ollama():
        try:
            ollama_cmd = find_ollama() or 'ollama'
            result = subprocess.run([ollama_cmd, 'pull', model_id],
                                  env=env, timeout=1800)
            if result.returncode == 0:
                print(f'    {green("OK")} Model downloaded.')
            else:
                print(yellow('    WARNING: Model pull may have failed.'))
        except subprocess.TimeoutExpired:
            print(yellow('    WARNING: Model download timed out.'))
        finally:
            if ollama_proc:
                kill_pid(ollama_proc.pid)
    print()

    # Step 3: Create Python venv
    print(f'  {cyan("[3/5]")} Creating Python virtual environment...')
    if not os.path.exists(VENV_DIR):
        try:
            subprocess.run([sys.executable, '-m', 'venv', VENV_DIR], check=True, timeout=120)
            print(f'    {green("OK")} Virtual environment created.')
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(red(f'    ERROR: Failed to create venv: {e}'))
            return False
    else:
        print(f'    {green("OK")} Virtual environment already exists.')
    print()

    # Step 4: Install dependencies
    print(f'  {cyan("[4/5]")} Installing Python dependencies...')
    req_file = os.path.join(APP_DIR, 'requirements.txt')
    try:
        subprocess.run([pip_executable(), 'install', '-r', req_file],
                      check=True, timeout=300, capture_output=True)
        print(f'    {green("OK")} Dependencies installed.')
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(red(f'    ERROR: Failed to install dependencies: {e}'))
        return False
    print()

    # Step 5: Initialize database
    print(f'  {cyan("[5/5]")} Initializing database...')
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        import sqlite3
        db = sqlite3.connect(DB_PATH)
        db.execute('PRAGMA journal_mode=OFF')
        db.execute('PRAGMA synchronous=OFF')
        with open(SCHEMA_PATH, 'r') as f:
            db.executescript(f.read())
        db.close()
        print(f'    {green("OK")} Database initialized.')
    else:
        import sqlite3
        db = sqlite3.connect(DB_PATH)
        with open(SCHEMA_PATH, 'r') as f:
            try:
                db.executescript(f.read())
            except sqlite3.OperationalError:
                pass
        db.close()
        print(f'    {green("OK")} Database already exists (schema updated).')
    print()

    # Success!
    print(green('=' * 56))
    print(green('|') + bold('    Setup Complete!'.center(54)) + green('|'))
    print(green('=' * 56))
    print()
    print(f'  Model:    {bold(model_id)}')
    print(f'  Port:     {bold(str(config.get("port", 5001)))}')
    print(f'  Config:   {dim(CONFIG_PATH)}')
    print()
    print(f'  To start: {cyan("python launch.py start")}')
    print(f'  Login:    teacher / 1234')
    print()
    return True


# ============================================================
# SETUP
# ============================================================
def cmd_setup():
    """First-time setup: runs wizard if no config, otherwise runs setup directly."""
    cfg = load_config()
    if not cfg.get('setup_completed'):
        return cmd_wizard()

    model_id = cfg.get('model', 'phi3')
    print('=' * 50)
    print('  LearnQuest Setup')
    print(f'  Platform: {SYSTEM} ({platform.machine()})')
    print(f'  Model: {model_id}')
    print('=' * 50)
    print()
    return _run_setup(model_id)


# ============================================================
# START
# ============================================================
def cmd_start():
    """Start Ollama + Flask, open browser."""
    cfg = load_config()
    model_id = cfg.get('model', 'phi3')
    port = int(os.environ.get('LEARNQUEST_PORT', cfg.get('port', 5001)))

    print('=' * 50)
    print('  Starting LearnQuest...')
    print(f'  Model: {model_id} | Port: {port}')
    print('=' * 50)
    print()

    # Check venv exists
    if not os.path.exists(python_executable()):
        print('ERROR: Setup not complete. Run: python launch.py setup')
        return False

    # Ensure DB has latest schema
    if os.path.exists(DB_PATH) and os.path.exists(SCHEMA_PATH):
        import sqlite3
        db = sqlite3.connect(DB_PATH)
        with open(SCHEMA_PATH, 'r') as f:
            try:
                db.executescript(f.read())
            except sqlite3.OperationalError:
                pass
        db.close()

    os.makedirs(PID_DIR, exist_ok=True)
    env = os.environ.copy()
    env['OLLAMA_MODELS'] = MODELS_DIR
    env['LEARNQUEST_DB'] = DB_PATH
    env['LEARNQUEST_CONTENT'] = os.path.join(APP_DIR, 'content')
    env['LEARNQUEST_PROMPTS'] = os.path.join(APP_DIR, 'prompts')
    env['LEARNQUEST_PORT'] = str(port)
    env['LEARNQUEST_MODEL'] = model_id

    # Step 1: Start Ollama
    print('[1/3] Starting Ollama...')
    if ollama_running():
        print('  Ollama is already running.')
    else:
        ollama_cmd = find_ollama() or 'ollama'
        try:
            log_file = open(os.path.join(SCRIPT_DIR, '.ollama.log'), 'w')
            proc = subprocess.Popen([ollama_cmd, 'serve'],
                                   env=env,
                                   stdout=log_file,
                                   stderr=log_file)
            write_pid('ollama', proc.pid)
            time.sleep(2)
            print('  Ollama started.')
        except FileNotFoundError:
            print('  WARNING: Ollama not found. AI tutor will not work.')
            print('  Install from https://ollama.com/download')

    # Step 2: Start Flask
    print('[2/3] Starting LearnQuest server...')
    if port_in_use(port):
        print(f'  Port {port} is already in use. LearnQuest may already be running.')
    else:
        log_file = open(os.path.join(SCRIPT_DIR, '.flask.log'), 'w')
        proc = subprocess.Popen(
            [python_executable(), 'server.py'],
            cwd=APP_DIR,
            env=env,
            stdout=log_file,
            stderr=log_file
        )
        write_pid('flask', proc.pid)
        time.sleep(2)

        if process_alive(proc.pid):
            print('  LearnQuest server started.')
        else:
            print('  ERROR: Server failed to start. Check .flask.log')
            return False

    # Step 3: Open browser
    print('[3/3] Opening browser...')
    url = f'http://localhost:{port}'
    try:
        webbrowser.open(url)
    except Exception:
        pass

    print()
    print('=' * 50)
    print('  LearnQuest is running!')
    print(f'  Open {url}')
    print()
    print('  To stop: python launch.py stop')
    print('=' * 50)
    return True


# ============================================================
# STOP
# ============================================================
def cmd_stop():
    """Stop Flask and Ollama."""
    print('=' * 50)
    print('  Stopping LearnQuest...')
    print('=' * 50)
    print()

    # Stop Flask
    flask_pid = read_pid('flask')
    if flask_pid and process_alive(flask_pid):
        print('  Stopping Flask server...')
        kill_pid(flask_pid)
        remove_pid('flask')
        print('  Flask stopped.')
    else:
        print('  Flask is not running.')
        remove_pid('flask')

    # Stop Ollama
    ollama_pid = read_pid('ollama')
    if ollama_pid and process_alive(ollama_pid):
        print('  Stopping Ollama...')
        kill_pid(ollama_pid)
        remove_pid('ollama')
        print('  Ollama stopped.')
    else:
        print('  Ollama was not started by us (or already stopped).')
        remove_pid('ollama')

    print()
    print('  LearnQuest stopped. Safe to remove USB.')
    return True


# ============================================================
# MAIN
# ============================================================
def main():
    args = sys.argv[1:]
    command = args[0] if args else 'start'

    if command == 'setup':
        success = cmd_setup()
    elif command == 'start':
        success = cmd_start()
    elif command == 'stop':
        success = cmd_stop()
    elif command == 'wizard':
        success = cmd_wizard()
    else:
        print(f'Unknown command: {command}')
        print('Usage: python launch.py [setup|start|stop|wizard]')
        success = False

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
