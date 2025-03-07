import os
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from PIL import Image, ImageTk
from datetime import datetime
import subprocess

# Directory where screenshots and notes are saved
SAVE_DIR = "screenshots_notes"


class ScreenshotNotesViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot Notes Viewer")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1)  # List panel
        self.main_frame.columnconfigure(1, weight=2)  # Preview panel
        self.main_frame.rowconfigure(0, weight=0)  # Header
        self.main_frame.rowconfigure(1, weight=1)  # Content
        
        # Create header with title and buttons
        self.create_header()
        
        # Create content section with list and preview
        self.create_content()
        
        # Load screenshots and notes
        self.load_screenshots_notes()

    def create_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="Screenshot Notes", font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT, padx=5)
        
        # Buttons frame (right aligned)
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        # Refresh button
        refresh_btn = ttk.Button(buttons_frame, text="Refresh", command=self.load_screenshots_notes)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Capture new button
        capture_btn = ttk.Button(buttons_frame, text="Capture New", command=self.capture_new)
        capture_btn.pack(side=tk.LEFT, padx=5)

    def create_content(self):
        # Create list panel (left side)
        list_frame = ttk.LabelFrame(self.main_frame, text="Screenshots")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Create list with scrollbar
        self.list_frame = ttk.Frame(list_frame)
        self.list_frame.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # List with items
        self.screenshots_list = tk.Listbox(
            self.list_frame,
            selectmode=tk.SINGLE,
            font=("Arial", 11),
            activestyle="none",
            height=20
        )
        self.screenshots_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Connect scrollbar to listbox
        self.screenshots_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.screenshots_list.yview)
        
        # Bind selection event
        self.screenshots_list.bind('<<ListboxSelect>>', self.on_item_select)
        
        # Create preview panel (right side)
        preview_frame = ttk.LabelFrame(self.main_frame, text="Preview")
        preview_frame.grid(row=1, column=1, sticky="nsew")
        preview_frame.rowconfigure(0, weight=3)  # Image
        preview_frame.rowconfigure(1, weight=1)  # Note
        preview_frame.columnconfigure(0, weight=1)
        
        # Image preview
        self.image_frame = ttk.Frame(preview_frame)
        self.image_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(expand=True)
        
        # Note preview
        note_frame = ttk.Frame(preview_frame)
        note_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        note_frame.columnconfigure(0, weight=1)
        note_frame.rowconfigure(0, weight=1)
        
        # Note text with scrollbar
        self.note_text = tk.Text(note_frame, wrap=tk.WORD, font=("Arial", 11), height=6)
        self.note_text.grid(row=0, column=0, sticky="nsew")
        
        note_scrollbar = ttk.Scrollbar(note_frame, command=self.note_text.yview)
        note_scrollbar.grid(row=0, column=1, sticky="ns")
        self.note_text.config(yscrollcommand=note_scrollbar.set)

        # Action buttons
        actions_frame = ttk.Frame(preview_frame)
        actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        self.open_btn = ttk.Button(actions_frame, text="Open in Finder", command=self.open_in_finder)
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(actions_frame, text="Delete", command=self.delete_item)
        self.delete_btn.pack(side=tk.LEFT, padx=5)

    def load_screenshots_notes(self):
        # Clear existing items
        self.screenshots_list.delete(0, tk.END)
        self.screenshots_data = []
        
        if not os.path.exists(SAVE_DIR):
            return
        
        # Get all PNG files
        files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.png')]
        files.sort(reverse=True)  # Sort by newest first
        
        for file in files:
            file_path = os.path.join(SAVE_DIR, file)
            note_path = file_path.replace('.png', '.txt')
            
            # Get file creation time
            try:
                creation_time = os.path.getctime(file_path)
                date_str = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
            except:
                date_str = "Unknown date"
            
            # Add to data list
            self.screenshots_data.append({
                'file_path': file_path,
                'note_path': note_path,
                'date': date_str,
                'filename': file
            })
            
            # Add to listbox
            display_name = f"{date_str} - {file}"
            self.screenshots_list.insert(tk.END, display_name)
        
        # Clear preview if no items
        if not files:
            self.clear_preview()
        else:
            # Select first item
            self.screenshots_list.selection_set(0)
            self.on_item_select(None)

    def on_item_select(self, event):
        # Get selected index
        selection = self.screenshots_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        item = self.screenshots_data[index]
        
        # Update image preview
        try:
            img = Image.open(item['file_path'])
            
            # Calculate maximum size for preview while maintaining aspect ratio
            max_width = 500
            max_height = 300
            img_width, img_height = img.size
            
            if img_width > max_width or img_height > max_height:
                ratio = min(max_width / img_width, max_height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep a reference
        except Exception as e:
            self.image_label.config(image='')
            print(f"Error loading image: {e}")
        
        # Update note text
        self.note_text.config(state=tk.NORMAL)
        self.note_text.delete(1.0, tk.END)
        
        if os.path.exists(item['note_path']):
            try:
                with open(item['note_path'], 'r') as f:
                    note_content = f.read()
                self.note_text.insert(tk.END, note_content)
            except Exception as e:
                self.note_text.insert(tk.END, f"Error loading note: {e}")
        else:
            self.note_text.insert(tk.END, "No note for this screenshot.")
        
        self.note_text.config(state=tk.DISABLED)

    def clear_preview(self):
        """Clear the preview panel"""
        self.image_label.config(image='')
        self.note_text.config(state=tk.NORMAL)
        self.note_text.delete(1.0, tk.END)
        self.note_text.insert(tk.END, "No screenshot selected.")
        self.note_text.config(state=tk.DISABLED)

    def open_in_finder(self):
        """Open the selected screenshot in Finder"""
        selection = self.screenshots_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        item = self.screenshots_data[index]
        
        # Use macOS 'open' command to reveal file in Finder
        subprocess.run(['open', '-R', item['file_path']])

    def delete_item(self):
        """Delete the selected screenshot and its note"""
        selection = self.screenshots_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        item = self.screenshots_data[index]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this screenshot and its note?",
            parent=self.root
        )
        
        if confirm:
            try:
                # Delete image file
                if os.path.exists(item['file_path']):
                    os.remove(item['file_path'])
                
                # Delete note file
                if os.path.exists(item['note_path']):
                    os.remove(item['note_path'])
                
                # Refresh the list
                self.load_screenshots_notes()
                messagebox.showinfo("Success", "Screenshot and note deleted successfully.", parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}", parent=self.root)

    def capture_new(self):
        """Capture a new screenshot using the functionality from the main script"""
        try:
            # Import functions from the main script
            from screenshot_notes import capture_screenshot, create_note_dialog
            
            # Minimize the viewer window to not interfere with screenshot
            self.root.iconify()
            
            # Wait a moment for the window to minimize
            self.root.after(500, lambda: self._perform_capture(capture_screenshot, create_note_dialog))
        except ImportError as e:
            messagebox.showerror(
                "Error", 
                f"Could not import from screenshot_notes.py: {str(e)}",
                parent=self.root
            )
    
    def _perform_capture(self, capture_screenshot, create_note_dialog):
        """Actually perform the screenshot capture using the imported functions"""
        # Capture the screenshot
        screenshot_path = capture_screenshot()
        if not screenshot_path:
            messagebox.showerror("Error", "Failed to capture screenshot", parent=self.root)
            self.root.deiconify()  # Show the window again
            return
        
        # Create note dialog
        note = create_note_dialog(self.root, screenshot_path)
        if note:
            note_file = screenshot_path.replace(".png", ".txt")
            with open(note_file, "w") as f:
                f.write(note)
            
            # Refresh the list
            self.load_screenshots_notes()
            
            # Select the newly added screenshot (should be at the top)
            if self.screenshots_data:
                self.screenshots_list.selection_set(0)
                self.on_item_select(None)
                
            messagebox.showinfo("Success", "Screenshot and note saved successfully!", parent=self.root)
        else:
            # If they canceled the note, we should still refresh to show the screenshot
            self.load_screenshots_notes()
            
        # Show the window again
        self.root.deiconify()
        self.root.lift()


def main():
    root = tk.Tk()
    app = ScreenshotNotesViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main() 