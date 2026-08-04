import ctypes
import ctypes.wintypes
import tkinter as tk

# Load libraries
user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

# Constants
ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003
ABE_BOTTOM = 3
SPI_GETWORKAREA = 0x0030

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

def get_work_area():
    rect = RECT()
    user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    print(f"Work area: top={rect.top}, bottom={rect.bottom}, left={rect.left}, right={rect.right}")
    return rect

def register_appbar(hwnd, height):
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    abd.uEdge = ABE_BOTTOM

    screen_width = user32.GetSystemMetrics(0)
    print(f"Screen width: {screen_width}")
    print(f"Target AppBar height: {height}")

    work_area = get_work_area()

    # Place AppBar *just above* the taskbar
    abd.rc.left = 0
    abd.rc.right = screen_width
    abd.rc.bottom = work_area.bottom
    abd.rc.top = work_area.bottom - height

    print(f"Initial AppBar rect: top={abd.rc.top}, bottom={abd.rc.bottom}, "
          f"left={abd.rc.left}, right={abd.rc.right}")

    shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(abd))
    shell32.SHAppBarMessage(ABM_QUERYPOS, ctypes.byref(abd))
    shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(abd))

    print(f"Final AppBar rect after ABM_SETPOS: top={abd.rc.top}, bottom={abd.rc.bottom}, "
          f"left={abd.rc.left}, right={abd.rc.right}")

    result = user32.SetWindowPos(
        hwnd,
        -1,  # HWND_TOPMOST
        abd.rc.left,
        abd.rc.top,
        abd.rc.right - abd.rc.left,
        abd.rc.bottom - abd.rc.top,
        0
    )

    if not result:
        print("SetWindowPos failed.")
    else:
        print(f"Window positioned successfully (hWnd={hwnd})")

def unregister_appbar(hwnd):
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    shell32.SHAppBarMessage(ABM_REMOVE, ctypes.byref(abd))
    print("AppBar unregistered.")

# === GUI ===
root = tk.Tk()
root.title("My 20px AppBar Above Taskbar")
root.configure(bg="darkblue")
root.overrideredirect(False)
root.wm_attributes("-topmost", True)

# Get window handle correctly
hwnd = root.winfo_id()
print(f"Window handle (HWND): {hwnd}")

# Fixed 20-pixel height
fixed_height = 50
# Delay registration until window is fully drawn
root.after(100, lambda: register_appbar(hwnd, fixed_height))

# Handle close event
def on_close():
    unregister_appbar(hwnd)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# Add label
label = tk.Label(
    root,
    text=f"My Custom 20px AppBar",
    fg="white",
    bg="darkblue",
    font=("Segoe UI", 10)
)
label.pack(padx=5, pady=2)

root.mainloop()
