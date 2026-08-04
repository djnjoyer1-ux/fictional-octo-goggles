import ctypes
import ctypes.wintypes
import tkinter as tk

# Load libraries
user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

# Constants for SHAppBarMessage
ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003

ABE_BOTTOM = 3

# RECT structure
class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.wintypes.LONG),
        ("top", ctypes.wintypes.LONG),
        ("right", ctypes.wintypes.LONG),
        ("bottom", ctypes.wintypes.LONG)
    ]

# APPBARDATA structure
class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.wintypes.DWORD),
        ("hWnd", ctypes.wintypes.HWND),
        ("uCallbackMessage", ctypes.wintypes.UINT),
        ("uEdge", ctypes.wintypes.UINT),
        ("rc", RECT),
        ("lParam", ctypes.wintypes.LPARAM)
    ]

def get_taskbar_height():
    # Taskbar class name is "Shell_TrayWnd"
    hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    if not hwnd:
        return 40  # fallback default

    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))

    height = rect.bottom - rect.top
    return height

def register_appbar(hwnd, height):
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    abd.uEdge = ABE_BOTTOM

    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # Place our AppBar above the taskbar
    abd.rc.left = 0
    abd.rc.right = screen_width
    abd.rc.bottom = screen_height
    abd.rc.top = screen_height - height

    shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(abd))
    shell32.SHAppBarMessage(ABM_QUERYPOS, ctypes.byref(abd))
    shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(abd))

    # Actually move the window
    user32.SetWindowPos(
        hwnd,
        -1,  # HWND_TOPMOST
        abd.rc.left,
        abd.rc.top,
        abd.rc.right - abd.rc.left,
        abd.rc.bottom - abd.rc.top,
        0
    )

def unregister_appbar(hwnd):
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    shell32.SHAppBarMessage(ABM_REMOVE, ctypes.byref(abd))

# === GUI ===
root = tk.Tk()
root.title("My AppBar (Matches Taskbar Height)")
root.configure(bg="darkblue")
root.overrideredirect(False)
root.wm_attributes("-topmost", True)

# Get window handle
hwnd = user32.GetParent(root.winfo_id())

# Measure the actual taskbar height
taskbar_height = get_taskbar_height()

# Register our AppBar at that height
register_appbar(hwnd, taskbar_height)

# Handle close event
def on_close():
    unregister_appbar(hwnd)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# Add label
label = tk.Label(
    root,
    text=f"My Custom AppBar (Height: {taskbar_height}px)",
    fg="white",
    bg="darkblue",
    font=("Segoe UI", 12)
)
label.pack(padx=10, pady=5)

root.mainloop()
