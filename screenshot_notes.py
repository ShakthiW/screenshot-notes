import os
from datetime import datetime
import tkinter as tk
import subprocess
from PIL import Image, ImageTk
from pynput import keyboard

# Directory to save screenshots and notes
SAVE_DIR = "screenshots_notes"
os.makedirs(SAVE_DIR, exist_ok=True)

def capture_screenshot():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(SAVE_DIR, f"screenshot_{timestamp}.png")
        # Use macOS screencapture command
        subprocess.run(['screencapture', '-x', file_path], check=True, timeout=5)
        if os.path.exists(file_path):
            optimize_image(file_path)
            return file_path
        return None
    except subprocess.TimeoutExpired:
        print("Screenshot capture timed out")
        return None
    except Exception as e:
        print(f"Error taking screenshot: {str(e)}")
        return None

def optimize_image(image_path):
    try:
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            max_size = 1500
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            img.save(image_path, 'PNG', optimize=True, quality=85)
    except Exception as e:
        print(f"Error optimizing image: {str(e)}")

def create_note_dialog(root, screenshot_path):
    """Creates a note dialog with a screenshot preview using a Toplevel window."""
    note_text = None

    def on_save():
        nonlocal note_text
        note_text = text_entry.get("1.0", "end-1c")
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    dialog = tk.Toplevel(root)
    dialog.title("Add Note")
    dialog.attributes("-topmost", True)
    
    # Set dialog size and center it on screen
    window_width = 400
    window_height = 400  # Increased height to accommodate image preview
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Load and display the screenshot preview
    try:
        img = Image.open(screenshot_path)
        max_preview_size = (200, 200)
        img.thumbnail(max_preview_size, Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        image_label = tk.Label(dialog, image=img_tk)
        image_label.image = img_tk  # Keep a reference
        image_label.pack(pady=5)
    except Exception as e:
        print("Error loading image preview:", e)

    # Label for note input
    label = tk.Label(dialog, text="Enter your note:", font=("Arial", 12))
    label.pack(pady=5)

    # Text entry for note
    text_entry = tk.Text(dialog, height=5, width=40, font=("Arial", 11))
    text_entry.pack(pady=5)

    # Frame for buttons
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)

    save_button = tk.Button(button_frame, text="Save", command=on_save, width=10)
    save_button.pack(side=tk.LEFT, padx=5)
    cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel, width=10)
    cancel_button.pack(side=tk.LEFT, padx=5)

    text_entry.focus_set()
    dialog.wait_window()  # Wait for the dialog to close
    return note_text

def process_screenshot_note(root):
    print("Trigger detected! Capturing screenshot...")
    screenshot_path = capture_screenshot()
    if not screenshot_path:
        print("Failed to capture screenshot")
        return

    note = create_note_dialog(root, screenshot_path)
    if note:
        note_file = screenshot_path.replace(".png", ".txt")
        with open(note_file, "w") as f:
            f.write(note)
        print(f"Note saved: {note_file}")
    else:
        print("No note added.")
    print(f"Screenshot saved: {screenshot_path}")

def on_activate(root):
    print("Hotkey detected!")
    # Schedule UI work on the main thread
    root.after(0, process_screenshot_note, root)

def for_canonical(f):
    return lambda k: f(listener.canonical(k))

def check_permissions():
    try:
        from pynput import keyboard  # just to re-verify permissions
        with keyboard.Listener(on_press=lambda k: None) as listener:
            if not listener.is_alive():
                print("\nERROR: Accessibility permissions required!")
                print("Please grant accessibility permissions to Terminal/IDE in:")
                print("System Settings -> Privacy & Security -> Accessibility\n")
                return False
        return True
    except Exception as e:
        print(f"Permission check failed: {str(e)}")
        return False

if __name__ == "__main__":
    if not check_permissions():
        print("Please grant accessibility permissions and try again.")
        exit(1)

    # Create a persistent Tk root (in the main thread)
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    print("Starting screenshot note tool...")

    hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('<cmd>+<shift>+6'),
        lambda: on_activate(root)
    )

    with keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release)) as listener:
        print("Running... Press Cmd+Shift+S to capture screenshot and add a note.")
        try:
            # Start the Tkinter main loop in the main thread
            root.mainloop()
        except KeyboardInterrupt:
            print("\nExiting gracefully...")
        except Exception as e:
            print(f"Error: {str(e)}")
    try:
        root.destroy()
    except Exception:
        pass
