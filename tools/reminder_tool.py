from crewai.tools import BaseTool
import subprocess
from typing import Optional
from pydantic import Field

class ReminderTool(BaseTool):
    """Tool to set reminders using AppleScript."""
    
    name: str = "ReminderTool"
    description: str = "A tool to set reminders with a specific time and note"
    
    note: str = Field(default="", description="The note content for the reminder")
    time: str = Field(default="", description="The time for the reminder in format YYYY-MM-DD HH:MM:SS")
    
    def update_parameters(self, note: Optional[str] = None, time: Optional[str] = None):
        """Update the reminder parameters at runtime"""
        if note:
            self.note = note
        if time:
            self.time = time
        return self

    def execute(self, note: Optional[str] = None, time: Optional[str] = None):
        # Update parameters if provided
        if note or time:
            self.update_parameters(note, time)
            
        # AppleScript to create a reminder
        applescript = f'''
        tell application "Reminders"
            set newReminder to make new reminder with properties {{name:"{self.note}", remind me date:date "{self.time}"}}
        end tell
        '''
        subprocess.run(['osascript', '-e', applescript])
        return f"Reminder set successfully: {self.note} at {self.time}"

    def _run(self, note: Optional[str] = None, time: Optional[str] = None):
        return self.execute(note, time)
