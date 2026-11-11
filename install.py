#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║          CloneWeb - Installer and Launcher           ║
║        Cyberpunk Neon Edition - Termux No Root       ║
║                  Created by Mr.X                     ║
╚══════════════════════════════════════════════════════╝
"""

import os
import re
import sys
import time
import shutil
import platform
import subprocess
import importlib.util


# Enable ANSI escape codes on Windows terminals
if platform.system() == 'Windows':
    try:
        os.system('')
    except Exception:
        pass


# ═══════════════ COLOR PALETTE (Neon Cyberpunk) ═══════════════
class C:
    PINK   = '\033[38;5;205m'
    CYAN   = '\033[38;5;51m'
    PURPLE = '\033[38;5;141m'
    GREEN  = '\033[38;5;46m'
    YELLOW = '\033[38;5;226m'
    RED    = '\033[38;5;196m'
    BLUE   = '\033[38;5;39m'
    ORANGE = '\033[38;5;208m'
    GRAY   = '\033[38;5;244m'
    BOLD   = '\033[1m'
    RESET  = '\033[0m'


# ═══════════════ PROMPT CONFIG ═══════════════
PROMPT_SYMBOL = "\u276F"        # ❯
PROMPT_USER   = "root"          # shown before @
PROMPT_HOST   = "installer"     # shown after @

VERSION = "1.0"


# ═══════════════ AUTHOR INFO ═══════════════
AUTHOR_INFO = {
    "Author":   "Mr.X",
    "Website":  "https://whomrx.pages.dev",
    "GitHub":   "https://github.com/Whomrx666",
}

# Path to the main tool that this installer manages
MAIN_TOOL_FILENAME = "cloneweb.py"


# ═══════════════ UTIL ═══════════════
ANSI_RE = re.compile(r'\033\[[0-9;]*m')


def vlen(s):
    """Return visible length of a string (ANSI codes excluded)."""
    return len(ANSI_RE.sub('', s))


def pad(s, n, align='left'):
    """Pad string to visual length n (ANSI-safe)."""
    d = n - vlen(s)
    if d < 0:
        d = 0
    if align == 'center':
        left = d // 2
        return ' ' * left + s + ' ' * (d - left)
    if align == 'right':
        return ' ' * d + s
    return s + ' ' * d


def truncate(s, n):
    """Truncate a plain string to n chars with ellipsis."""
    if len(s) <= n:
        return s
    return s[:max(0, n - 3)] + "..."


def term_width():
    """Get terminal width (fallback 80)."""
    try:
        w = shutil.get_terminal_size(fallback=(80, 24)).columns
    except Exception:
        w = 80
    return max(50, w - 1)


def clear():
    """Clear the terminal screen (works on Windows, Linux, macOS, Termux)."""
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


# ═══════════════ BOX HELPERS ═══════════════
def box_top(w, color=None):
    color = color or C.PINK
    return f"{color}┌{'─' * (w - 2)}┐{C.RESET}"


def box_mid(w, color=None):
    color = color or C.PINK
    return f"{color}├{'─' * (w - 2)}┤{C.RESET}"


def box_bot(w, color=None):
    color = color or C.PINK
    return f"{color}└{'─' * (w - 2)}┘{C.RESET}"


def box_row(content, w, align='left', color=None):
    color = color or C.PINK
    return f"{color}│{C.RESET} {pad(content, w - 4, align)} {color}│{C.RESET}"


# ═══════════════ PROMPT ═══════════════
def build_prompt_strings():
    """Build the two-line terminal prompt strings:
        ┌─(root@installer)
        └─❯ 
    """
    border = C.PINK

    user_str = f"{C.GREEN}{C.BOLD}{PROMPT_USER}{C.RESET}"
    at_str   = f"{C.GRAY}@{C.RESET}"
    host_str = f"{C.CYAN}{PROMPT_HOST}{C.RESET}"

    line1 = (
        f"{border}┌─({C.RESET}"
        f"{user_str}{at_str}{host_str}"
        f"{border}){C.RESET}"
    )
    line2 = (
        f"{border}└─{C.RESET}"
        f"{C.PINK}{C.BOLD}{PROMPT_SYMBOL}{C.RESET}"
        f" {C.GREEN}"
    )
    return line1, line2


def print_prompt():
    """Print the two-line terminal prompt and leave cursor ready for input."""
    line1, line2 = build_prompt_strings()
    sys.stdout.write(f"{line1}\n")
    sys.stdout.write(line2)
    sys.stdout.flush()


def end_prompt():
    """Reset color after user input."""
    sys.stdout.write(f"{C.RESET}")
    sys.stdout.flush()


def ask_yes_no(prompt_text, default=None):
    """Ask a yes/no question. Return True for yes, False for no."""
    print()
    print(box_top(term_width(), C.YELLOW))
    print(box_row(
        f"{C.YELLOW}{C.BOLD}{PROMPT_SYMBOL}{C.RESET} {C.CYAN}{prompt_text} "
        f"{C.GRAY}(y/n){C.RESET}",
        term_width()
    ))
    print(box_bot(term_width(), C.YELLOW))
    print_prompt()
    try:
        ans = input().strip().lower()
    except (KeyboardInterrupt, EOFError):
        end_prompt()
        return False
    end_prompt()

    if not ans and default is not None:
        return default
    return ans in ("y", "ya", "yes")


# ═══════════════ INSTALLER BANNER (different from CloneWeb) ═══════════════
INSTALLER_ART = r"""
▗▄▄▄▖▗▖  ▗▖ ▗▄▄▖▗▄▄▄▖▗▄▖ ▗▖   ▗▖   ▗▄▄▄▖▗▄▄▖ 
  █  ▐▛▚▖▐▌▐▌     █ ▐▌ ▐▌▐▌   ▐▌   ▐▌   ▐▌ ▐▌
  █  ▐▌ ▝▜▌ ▝▀▚▖  █ ▐▛▀▜▌▐▌   ▐▌   ▐▛▀▀▘▐▛▀▚▖
▗▄█▄▖▐▌  ▐▌▗▄▄▞▘  █ ▐▌ ▐▌▐▙▄▄▖▐▙▄▄▖▐▙▄▄▖▐▌ ▐▌"""


def banner():
    """Display the installer banner (distinct from the main tool banner)."""
    w = term_width()

    # ASCII art with neon gradient (pink -> purple -> cyan -> blue)
    art_lines = INSTALLER_ART.split("\n")
    color_cycle = [C.PINK, C.PURPLE, C.CYAN, C.BLUE]

    for i, line in enumerate(art_lines):
        # Skip empty trailing lines
        if not line.strip():
            continue
        col = color_cycle[i % len(color_cycle)]
        print(f"{col}{C.BOLD}{line.center(w)}{C.RESET}")

    print()

    # Subtitle box
    print(box_top(w, C.PURPLE))
    print(box_row(
        f"{C.YELLOW}{C.BOLD}[ CLONEWEB - INSTALLER AND LAUNCHER v{VERSION} ]{C.RESET}",
        w, 'center', C.PURPLE
    ))
    print(box_mid(w, C.PURPLE))
    print(box_row(
        f"{C.CYAN}Theme    {C.GRAY}: {C.PURPLE}Cyberpunk Neon{C.RESET}",
        w, 'left', C.PURPLE
    ))
    print(box_row(
        f"{C.CYAN}Platform {C.GRAY}: {C.PURPLE}Termux / Linux / macOS / Windows{C.RESET}",
        w, 'left', C.PURPLE
    ))
    print(box_row(
        f"{C.CYAN}Author   {C.GRAY}: {C.GREEN}{C.BOLD}{AUTHOR_INFO['Author']}{C.RESET}",
        w, 'left', C.PURPLE
    ))
    print(box_bot(w, C.PURPLE))
    print()


# ═══════════════ STEP HEADER ═══════════════
def print_step_header(w, step_num, total_steps, title, color=None):
    """Print a 'STEP X/Y' header box."""
    color = color or C.PINK
    print(box_top(w, color))
    print(box_row(
        f"{C.YELLOW}{C.BOLD}[ STEP {step_num}/{total_steps} ]{C.RESET} {C.GREEN}{title}{C.RESET}",
        w, 'left', color
    ))
    print(box_mid(w, color))


# ═══════════════ ENVIRONMENT DETECTION ═══════════════
def detect_environment():
    """
    Detect:
      - Operating system and version
      - Terminal application (Termux, iTerm, VSCode, etc.)
      - User shell
      - System architecture
      - Available package manager
      - Whether the user runs Termux
    Returns a dict with all info.
    """
    env = {
        'os':              platform.system(),
        'os_release':      platform.release(),
        'os_name':         platform.system(),
        'machine':         platform.machine(),
        'python_ver':      platform.python_version(),
        'python_impl':     platform.python_implementation(),
        'shell':           os.environ.get('SHELL', '') or os.environ.get('COMSPEC', 'Unknown'),
        'terminal_app':    'Unknown',
        'is_termux':       False,
        'pkg_manager':     None,
        'pkg_manager_cmd': None,
    }

    # ─── Termux detection (highest priority) ───
    prefix = os.environ.get('PREFIX', '')
    termux_appdata = '/data/data/com.termux'
    if ('com.termux' in prefix) or os.path.exists(termux_appdata):
        env['is_termux'] = True
        env['terminal_app'] = 'Termux'
        env['os_name'] = 'Android (via Termux)'
        env['pkg_manager'] = 'pkg'
        env['pkg_manager_cmd'] = ['pkg', 'install', '-y']
        return env

    # ─── macOS ───
    if env['os'] == 'Darwin':
        tp = os.environ.get('TERM_PROGRAM', '')
        if not tp:
            tp = 'Terminal.app'
        env['terminal_app'] = tp
        env['os_name'] = f"macOS {platform.mac_ver()[0]}"
        if shutil.which('brew'):
            env['pkg_manager'] = 'brew'
            env['pkg_manager_cmd'] = ['brew', 'install']
        return env

    # ─── Windows ───
    if env['os'] == 'Windows':
        if os.environ.get('WT_SESSION'):
            env['terminal_app'] = 'Windows Terminal'
        elif os.environ.get('TERM_PROGRAM'):
            env['terminal_app'] = os.environ['TERM_PROGRAM']
        else:
            env['terminal_app'] = 'cmd / PowerShell'
        env['os_name'] = f"Windows {platform.release()}"
        if shutil.which('winget'):
            env['pkg_manager'] = 'winget'
            env['pkg_manager_cmd'] = ['winget', 'install']
        elif shutil.which('choco'):
            env['pkg_manager'] = 'choco'
            env['pkg_manager_cmd'] = ['choco', 'install', '-y']
        return env

    # ─── Linux (general) ───
    # Terminal application
    term_program = os.environ.get('TERM_PROGRAM', '')
    if term_program:
        env['terminal_app'] = term_program
    else:
        term = os.environ.get('TERM', '')
        if term:
            env['terminal_app'] = f"Linux Terminal ({term})"
        else:
            env['terminal_app'] = 'Linux Terminal'

    # Distribution
    os_name = 'Linux'
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('PRETTY_NAME='):
                        os_name = line.split('=', 1)[1].strip().strip('"')
                        break
                    elif line.startswith('NAME=') and os_name == 'Linux':
                        os_name = line.split('=', 1)[1].strip().strip('"')
    except Exception:
        pass
    env['os_name'] = os_name

    # Package manager
    for mgr, cmd in (
        ('apt-get', ['sudo', 'apt-get', 'install', '-y']),
        ('apt',     ['sudo', 'apt', 'install', '-y']),
        ('dnf',     ['sudo', 'dnf', 'install', '-y']),
        ('yum',     ['sudo', 'yum', 'install', '-y']),
        ('pacman',  ['sudo', 'pacman', '-S', '--noconfirm']),
        ('zypper',  ['sudo', 'zypper', 'install', '-y']),
        ('apk',     ['sudo', 'apk', 'add']),
        ('nix-env', ['nix-env', '-iA']),
    ):
        if shutil.which(mgr):
            env['pkg_manager'] = mgr
            env['pkg_manager_cmd'] = cmd
            break

    return env


def show_environment(w, env):
    """Display the environment info inside a box."""
    print(box_row(f"{C.CYAN}OS          {C.GRAY}: {C.YELLOW}{env['os_name']}{C.RESET}", w, 'left', C.PINK))
    print(box_row(f"{C.CYAN}Terminal    {C.GRAY}: {C.YELLOW}{env['terminal_app']}{C.RESET}", w, 'left', C.PINK))
    print(box_row(f"{C.CYAN}Shell       {C.GRAY}: {C.YELLOW}{truncate(env['shell'], w - 18)}{C.RESET}", w, 'left', C.PINK))
    print(box_row(f"{C.CYAN}Architecture{C.GRAY}: {C.YELLOW}{env['machine']}{C.RESET}", w, 'left', C.PINK))
    print(box_row(f"{C.CYAN}Python      {C.GRAY}: {C.YELLOW}{env['python_impl']} {env['python_ver']}{C.RESET}", w, 'left', C.PINK))
    pkg = env['pkg_manager'] if env['pkg_manager'] else 'not detected'
    print(box_row(f"{C.CYAN}Package Mgr {C.GRAY}: {C.YELLOW}{pkg}{C.RESET}", w, 'left', C.PINK))


# ═══════════════ PACKAGE DETECTION ═══════════════
def is_module_installed(module_name):
    """
    Check if a Python module is importable in the current interpreter.
    Uses importlib.util.find_spec which is fast and reliable.
    """
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False
    except Exception:
        return False


def verify_module_via_subprocess(module_name):
    """
    Verify a module by launching a fresh Python interpreter and importing it.
    This is the most reliable check after a pip install.
    """
    try:
        proc = subprocess.run(
            [sys.executable, '-c', f'import {module_name}'],
            capture_output=True, text=True, timeout=30
        )
        return proc.returncode == 0
    except Exception:
        return False


# ═══════════════ PIP DETECTION ═══════════════
def check_pip():
    """
    Check if pip is available for the current Python.
    Returns (available: bool, version_str: str).
    """
    try:
        proc = subprocess.run(
            [sys.executable, '-m', 'pip', '--version'],
            capture_output=True, text=True, timeout=30
        )
        if proc.returncode == 0:
            return True, proc.stdout.strip()
    except Exception:
        pass
    return False, ''


def ensure_pip(env):
    """
    Try to install pip if missing.
    Returns True if pip is available afterwards, False otherwise.
    """
    ok, _ = check_pip()
    if ok:
        return True

    print(f"{C.YELLOW}   [i] pip not found, attempting to install...{C.RESET}")

    # Try ensurepip first (works on all standard Python installs)
    try:
        proc = subprocess.run(
            [sys.executable, '-m', 'ensurepip', '--upgrade'],
            capture_output=True, text=True, timeout=180
        )
        if proc.returncode == 0:
            ok, _ = check_pip()
            if ok:
                return True
    except Exception:
        pass

    # Try OS-level install
    if env['is_termux']:
        try:
            proc = subprocess.run(
                ['pkg', 'install', '-y', 'python-pip'],
                capture_output=True, text=True, timeout=300
            )
            if proc.returncode == 0:
                ok, _ = check_pip()
                if ok:
                    return True
        except Exception:
            pass
    elif env['pkg_manager_cmd']:
        try:
            cmd = env['pkg_manager_cmd'] + ['python3-pip']
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if proc.returncode == 0:
                ok, _ = check_pip()
                if ok:
                    return True
        except Exception:
            pass

    return False


# ═══════════════ PACKAGE INSTALLATION ═══════════════
def install_via_pip(pip_name):
    """
    Install a Python package via pip. Tries several fallbacks:
      1. pip install --upgrade <name>
      2. pip install --user --upgrade <name>
      3. pip install --user --break-system-packages --upgrade <name>
      4. pip install --break-system-packages --upgrade <name>
      5. pip (as executable)
      6. pip3 (as executable)
    Returns (success: bool, used_command: str or None).
    """
    candidates = [
        [sys.executable, '-m', 'pip', 'install', '--upgrade', pip_name],
        [sys.executable, '-m', 'pip', 'install', '--user', '--upgrade', pip_name],
        [sys.executable, '-m', 'pip', 'install', '--user',
         '--break-system-packages', '--upgrade', pip_name],
        [sys.executable, '-m', 'pip', 'install',
         '--break-system-packages', '--upgrade', pip_name],
    ]

    if shutil.which('pip'):
        candidates.append(['pip', 'install', '--user', pip_name])
    if shutil.which('pip3'):
        candidates.append(['pip3', 'install', '--user', pip_name])

    for cmd in candidates:
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            if proc.returncode == 0:
                return True, ' '.join(cmd)
        except Exception:
            continue

    return False, None


def show_package_status(w, packages):
    """
    Print each package with its status inside a box.
    packages: list of (pip_name, import_name, is_installed).
    Returns count of missing packages.
    """
    missing_count = 0
    for pip_name, import_name, installed in packages:
        if installed:
            marker = f"{C.GREEN}[+]{C.RESET}"
            status = f"{C.GREEN}installed{C.RESET}"
        else:
            marker = f"{C.RED}[-]{C.RESET}"
            status = f"{C.YELLOW}missing{C.RESET}"
            missing_count += 1

        name_padded = pad(pip_name, 20)
        print(box_row(
            f"{marker} {C.CYAN}{name_padded}{C.RESET} {C.GRAY}->{C.RESET} {status}",
            w, 'left', C.PINK
        ))
    return missing_count


# ═══════════════ SPINNER ═══════════════
def show_spinner_line(text, duration=0.8):
    """Show a short spinner animation inline."""
    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    start = time.time()
    i = 0
    try:
        while time.time() - start < duration:
            frame = frames[i % len(frames)]
            sys.stdout.write(f"\r   {C.PINK}{C.BOLD}{frame}{C.RESET} {C.CYAN}{text}{C.RESET}    ")
            sys.stdout.flush()
            time.sleep(0.06)
            i += 1
        sys.stdout.write("\r" + " " * 70 + "\r")
        sys.stdout.flush()
    except KeyboardInterrupt:
        sys.stdout.write("\r" + " " * 70 + "\r")
        sys.stdout.flush()


# ═══════════════ LAUNCH LOGIC ═══════════════
def locate_main_tool():
    """
    Locate cloneweb.py in the same directory as this installer.
    Returns absolute path if found, else None.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(script_dir, MAIN_TOOL_FILENAME)
    if os.path.isfile(candidate):
        return candidate
    return None


def launch_main_tool(tool_path):
    """
    Launch cloneweb.py using the same Python interpreter.
    The child process inherits the terminal; installer waits for it.
    Returns the exit code.
    """
    try:
        proc = subprocess.run([sys.executable, tool_path])
        return proc.returncode
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"{C.RED}[!] Failed to launch: {e}{C.RESET}")
        return 1


# ═══════════════ COOL GOODBYE (short) ═══════════════
def cool_goodbye(message_lines=None):
    """
    Show a brief neon goodbye.
    message_lines: optional list of (color, bold, text) tuples.
    """
    try:
        clear()
    except Exception:
        pass

    w = term_width()

    if message_lines is None:
        message_lines = [
            (C.PINK,   C.BOLD, "Setup complete."),
            (C.CYAN,   "",     "You can run CloneWeb anytime."),
            (C.PURPLE, "",     "Happy cloning!"),
        ]

    print()
    print(f"{C.PURPLE}{'═' * (w - 2)}{C.RESET}")
    print()

    for color, bold, text in message_lines:
        print(f"{color}{bold}{text.center(w)}{C.RESET}")
        time.sleep(0.35)

    print()
    print(f"{C.PURPLE}{'═' * (w - 2)}{C.RESET}")
    print()

    try:
        for dots in ('.', '..', '...'):
            sys.stdout.write(f"\r  {C.PINK}Closing installer{dots}{C.RESET}   ")
            sys.stdout.flush()
            time.sleep(0.3)
        sys.stdout.write(f"\r  {C.GREEN}Done.{C.RESET}                  \n")
        sys.stdout.flush()
    except KeyboardInterrupt:
        pass

    print()
    time.sleep(0.25)


# ═══════════════ MAIN ═══════════════
def main():
    total_steps = 4

    try:
        # Step 0: clean screen then show banner
        clear()
        banner()
        w = term_width()

        # ─── STEP 1: environment detection ───
        print_step_header(w, 1, total_steps, "Detecting environment", C.PINK)
        show_spinner_line("Scanning system...", 0.7)
        env = detect_environment()
        show_environment(w, env)
        print(box_bot(w, C.PINK))
        print(f"{C.GREEN}   [+] Environment detected{C.RESET}")
        print()

        # ─── STEP 2: Python version check ───
        print_step_header(w, 2, total_steps, "Checking Python version", C.PINK)
        show_spinner_line("Verifying Python...", 0.5)

        py_ver = env['python_ver']
        py_parts = tuple(int(x) for x in py_ver.split('.')[:2])
        min_required = (3, 7)
        is_compatible = py_parts >= min_required

        print(box_row(
            f"{C.CYAN}Required    {C.GRAY}: {C.YELLOW}Python {min_required[0]}.{min_required[1]}+{C.RESET}",
            w, 'left', C.PINK
        ))
        print(box_row(
            f"{C.CYAN}Detected    {C.GRAY}: {C.YELLOW}{env['python_impl']} {py_ver}{C.RESET}",
            w, 'left', C.PINK
        ))
        print(box_row(
            f"{C.CYAN}Status      {C.GRAY}: "
            + (f"{C.GREEN}compatible{C.RESET}" if is_compatible else f"{C.RED}too old{C.RESET}"),
            w, 'left', C.PINK
        ))
        print(box_bot(w, C.PINK))

        if not is_compatible:
            print(f"{C.RED}   [!] Python {min_required[0]}.{min_required[1]}+ is required.{C.RESET}")
            print(f"{C.YELLOW}   [i] Please upgrade Python and try again.{C.RESET}")
            cool_goodbye([
                (C.RED,  C.BOLD, "Installation aborted."),
                (C.GRAY, "",     "Python version is too old."),
            ])
            return
        print(f"{C.GREEN}   [+] Python version is compatible{C.RESET}")
        print()

        # ─── STEP 3: package check ───
        # Required packages: (pip_name, import_name)
        required_packages = [
            ('requests',           'requests'),
            ('beautifulsoup4',     'bs4'),
            ('urllib3',            'urllib3'),
            ('certifi',            'certifi'),
            ('charset-normalizer', 'charset_normalizer'),
        ]

        print_step_header(w, 3, total_steps, "Checking required Python packages", C.PINK)
        show_spinner_line("Scanning installed packages...", 0.7)

        package_status = []
        for pip_name, import_name in required_packages:
            installed = is_module_installed(import_name)
            package_status.append((pip_name, import_name, installed))

        missing = show_package_status(w, package_status)
        print(box_bot(w, C.PINK))

        if missing == 0:
            print(f"{C.GREEN}   [+] All required packages are already installed{C.RESET}")
            print(f"{C.GRAY}       (no installation needed){C.RESET}")
        else:
            print(f"{C.YELLOW}   [i] {missing} package(s) need to be installed{C.RESET}")
        print()

        # ─── STEP 4: install missing packages ───
        if missing > 0:
            print_step_header(w, 4, total_steps, "Installing missing packages", C.ORANGE)

            # Make sure pip is available
            pip_ok = ensure_pip(env)
            if not pip_ok:
                print(box_bot(w, C.ORANGE))
                print(f"{C.RED}   [!] pip is not available on this system.{C.RESET}")
                print(f"{C.YELLOW}   [i] Install pip manually and re-run this installer.{C.RESET}")
                cool_goodbye([
                    (C.RED,  C.BOLD, "Installation aborted."),
                    (C.GRAY, "",     "pip could not be installed."),
                ])
                return

            installed_success = 0
            installed_failed = []

            for pip_name, import_name, already_installed in package_status:
                if already_installed:
                    continue

                # Show progress for this package
                sys.stdout.write(
                    f"{C.PINK}   [>]{C.RESET} {C.CYAN}Installing "
                    f"{C.YELLOW}{pip_name}{C.CYAN}...{C.RESET}    "
                )
                sys.stdout.flush()

                ok, used_cmd = install_via_pip(pip_name)

                if ok:
                    # Verify by launching a fresh Python
                    verified = verify_module_via_subprocess(import_name)
                    if verified:
                        sys.stdout.write(f"{C.GREEN}[+]{C.RESET}\n")
                        sys.stdout.flush()
                        installed_success += 1
                    else:
                        sys.stdout.write(f"{C.YELLOW}[?]{C.RESET}\n")
                        sys.stdout.flush()
                        installed_success += 1
                else:
                    sys.stdout.write(f"{C.RED}[-]{C.RESET}\n")
                    sys.stdout.flush()
                    installed_failed.append(pip_name)

            print(box_bot(w, C.ORANGE))

            if installed_failed:
                print(f"{C.YELLOW}   [!] Some packages failed to install:{C.RESET}")
                for name in installed_failed:
                    print(f"{C.RED}       - {name}{C.RESET}")
                print(f"{C.GRAY}   [i] Try installing them manually:{C.RESET}")
                for name in installed_failed:
                    print(f"{C.GRAY}       {sys.executable} -m pip install {name}{C.RESET}")
            else:
                print(f"{C.GREEN}   [+] All packages installed successfully{C.RESET}")

            # Final verification pass
            print()
            print(f"{C.YELLOW}   [*] Verifying installation...{C.RESET}")
            still_missing = []
            for pip_name, import_name, _ in package_status:
                if not verify_module_via_subprocess(import_name):
                    still_missing.append(pip_name)

            if still_missing:
                print(f"{C.RED}   [!] Still missing: {', '.join(still_missing)}{C.RESET}")
                print(f"{C.GRAY}   [i] You may need to restart the terminal "
                      f"or reinstall manually.{C.RESET}")
            else:
                print(f"{C.GREEN}   [+] Verification passed - all packages are ready{C.RESET}")
        else:
            # No missing packages - still show step 4 as completed
            print_step_header(w, 4, total_steps, "Installation not needed", C.GREEN)
            print(box_row(
                f"{C.GREEN}All dependencies are already satisfied.{C.RESET}",
                w, 'left', C.GREEN
            ))
            print(box_bot(w, C.GREEN))
            print(f"{C.GREEN}   [+] Skipping installation step{C.RESET}")
        print()

        # ─── SUMMARY ───
        print(box_top(w, C.GREEN))
        print(box_row(
            f"{C.GREEN}{C.BOLD}{'INSTALLATION COMPLETE'.center(w - 4)}{C.RESET}",
            w, 'center', C.GREEN
        ))
        print(box_mid(w, C.GREEN))
        print(box_row(
            f"{C.CYAN}Status   {C.GRAY}: {C.GREEN}all dependencies satisfied{C.RESET}",
            w, 'left', C.GREEN
        ))
        print(box_row(
            f"{C.CYAN}Python   {C.GRAY}: {C.YELLOW}{env['python_impl']} {env['python_ver']}{C.RESET}",
            w, 'left', C.GREEN
        ))
        print(box_row(
            f"{C.CYAN}Terminal {C.GRAY}: {C.YELLOW}{env['terminal_app']}{C.RESET}",
            w, 'left', C.GREEN
        ))
        print(box_bot(w, C.GREEN))
        print()

        # ─── LAUNCH PROMPT ───
        tool_path = locate_main_tool()
        if tool_path is None:
            # cloneweb.py not found in this directory
            print(box_top(w, C.RED))
            print(box_row(
                f"{C.RED}{C.BOLD}MAIN TOOL NOT FOUND{C.RESET}",
                w, 'center', C.RED
            ))
            print(box_mid(w, C.RED))
            print(box_row(
                f"{C.GRAY}Expected '{MAIN_TOOL_FILENAME}' in the same "
                f"folder as this installer.{C.RESET}",
                w, 'left', C.RED
            ))
            print(box_row(
                f"{C.GRAY}Current folder:{C.RESET} "
                f"{C.YELLOW}{truncate(os.path.dirname(os.path.abspath(__file__)), w - 20)}{C.RESET}",
                w, 'left', C.RED
            ))
            print(box_bot(w, C.RED))
            print()
            print(f"{C.YELLOW}   [i] Place {MAIN_TOOL_FILENAME} next to install.py and re-run.{C.RESET}")
            cool_goodbye([
                (C.YELLOW, C.BOLD, "Setup complete, but main tool missing."),
                (C.GRAY,   "",     "Add cloneweb.py to launch it."),
            ])
            return

        # Ask user to launch
        launch_now = ask_yes_no(f"Launch {MAIN_TOOL_FILENAME} now?", default=False)

        if launch_now:
            print()
            print(box_top(w, C.CYAN))
            print(box_row(
                f"{C.CYAN}{C.BOLD}Launching {MAIN_TOOL_FILENAME}...{C.RESET}",
                w, 'center', C.CYAN
            ))
            print(box_row(
                f"{C.GRAY}Path: {truncate(tool_path, w - 12)}{C.RESET}",
                w, 'left', C.CYAN
            ))
            print(box_bot(w, C.CYAN))
            print()
            time.sleep(0.6)

            exit_code = launch_main_tool(tool_path)

            # After cloneweb.py exits, we are back here
            print()
            print(box_top(w, C.GRAY))
            print(box_row(
                f"{C.GRAY}CloneWeb exited with code: {C.YELLOW}{exit_code}{C.RESET}",
                w, 'left', C.GRAY
            ))
            print(box_bot(w, C.GRAY))

            cool_goodbye([
                (C.PINK, C.BOLD, "Thanks for using CloneWeb."),
                (C.CYAN, "",     "Come back anytime."),
            ])
        else:
            cool_goodbye([
                (C.PINK,   C.BOLD, "Setup complete."),
                (C.CYAN,   "",     "Run cloneweb.py whenever you are ready."),
                (C.PURPLE, "",     "Happy cloning!"),
            ])

    except KeyboardInterrupt:
        # Ctrl+C at any point -> clean goodbye
        print()
        try:
            cool_goodbye([
                (C.YELLOW, C.BOLD, "Installer interrupted."),
                (C.GRAY,   "",     "No changes were left unfinished."),
            ])
        except Exception:
            pass
        return
    except Exception as e:
        print(f"\n{C.RED}[!] Unexpected error: {type(e).__name__}: {e}{C.RESET}")
        try:
            cool_goodbye([
                (C.RED,  C.BOLD, "Installer failed."),
                (C.GRAY, "",     "See error above for details."),
            ])
        except Exception:
            pass
        return


if __name__ == "__main__":
    main()