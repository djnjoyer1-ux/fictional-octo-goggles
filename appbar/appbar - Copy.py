import ctypes
import ctypes.wintypes
import sys
import tkinter as tk

# Load shell32.dll
shell32 = ctypes.windll.shell32
user32 = ctypes.windll.user32

# Constants
ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003

ABE_BOTTOM = 3

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.wintypes.DWORD),
        ("hWnd", ctypes.wintypes.HWND),
        ("uCallbackMessage", ctypes.wintypes.UINT),
        ("uEdge", ctypes.wintypes.UINT),
        ("rc", ctypes.wintypes.RECT),
        ("lParam", ctypes.wintypes.LPARAM)
    ]

def register_appbar(hwnd, height=40):
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    abd.uEdge = ABE_BOTTOM

    # Get screen dimensions
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # Desired rectangle at bottom of screen
    abd.rc.left = 0
    abd.rc.right = screen_width
    abd.rc.bottom = screen_height
    abd.rc.top = screen_height - height

    shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(abd))
    shell32.SHAppBarMessage(ABM_QUERYPOS, ctypes.byref(abd))
    shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(abd))

    # Move the window to that position
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

# Tkinter UI setup
root = tk.Tk()
root.title("My AppBar")
root.configure(bg="darkblue")

# ✅ Allow window decorations (close/minimize/maximize)
root.overrideredirect(False)

# Stay on top
root.wm_attributes("-topmost", True)

# Get window handle
hwnd = ctypes.windll.user32.GetParent(root.winfo_id())

# Register it as an AppBar
register_appbar(hwnd, height=40)

# Clean up on close
def on_close():
    unregister_appbar(hwnd)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# Add some content
label = tk.Label(root, text="My Custom AppBar", fg="white", bg="darkblue", font=("Segoe UI", 12))
label.pack(padx=10, pady=5)

root.mainloop()
