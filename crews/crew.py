from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from tools.reminder_tool import ReminderTool
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput
from datetime import datetime
from dotenv import load_dotenv
import yaml
import os
from pydantic import BaseModel
from typing import Literal

load_dotenv()
web_search_tool = SerperDevTool()
# Initialize with empty values - will be updated during task execution
reminder_tool = ReminderTool()

# Define Pydantic models for task outputs
class TaskClassificationOutput(BaseModel):
    task_type: Literal['Summarize notes', 'Actions']
    notes: str
    screenshot: str

class SummarizeNotesOutput(BaseModel):
    notes: str
    screenshot: str
    summary: str

class ActionClassificationOutput(BaseModel):
    task_type: Literal['Actions']
    action: Literal['research', 'reminder', 'other']
    screenshot: str

# Define condition functions
def is_summary(output) -> bool:
    # Handle different types of output
    try:
        if hasattr(output, 'json'):
            if isinstance(output.json, dict):
                return output.json.get('task_type') == 'Summarize notes'
            elif isinstance(output.json, str):
                import json
                data = json.loads(output.json)
                return data.get('task_type') == 'Summarize notes'
        elif hasattr(output, 'pydantic') and output.pydantic:
            return output.pydantic.task_type == 'Summarize notes'
        elif isinstance(output, dict):
            return output.get('task_type') == 'Summarize notes'
        elif isinstance(output, str):
            # Try to parse as JSON
            import json
            data = json.loads(output)
            return data.get('task_type') == 'Summarize notes'
    except Exception as e:
        print(f"Error in is_summary: {e}")
    return False

def is_action(output) -> bool:
    # Handle different types of output
    try:
        if hasattr(output, 'json'):
            if isinstance(output.json, dict):
                return output.json.get('task_type') == 'Actions'
            elif isinstance(output.json, str):
                import json
                data = json.loads(output.json)
                return data.get('task_type') == 'Actions'
        elif hasattr(output, 'pydantic') and output.pydantic:
            return output.pydantic.task_type == 'Actions'
        elif isinstance(output, dict):
            return output.get('task_type') == 'Actions'
        elif isinstance(output, str):
            # Try to parse as JSON
            import json
            data = json.loads(output)
            return data.get('task_type') == 'Actions'
    except Exception as e:
        print(f"Error in is_action: {e}")
    return False

def is_research(output) -> bool:
    # Handle different types of output
    try:
        if hasattr(output, 'json'):
            if isinstance(output.json, dict):
                return output.json.get('action') == 'research'
            elif isinstance(output.json, str):
                import json
                data = json.loads(output.json)
                return data.get('action') == 'research'
        elif hasattr(output, 'pydantic') and output.pydantic:
            return getattr(output.pydantic, 'action', '') == 'research'
        elif isinstance(output, dict):
            return output.get('action') == 'research'
        elif isinstance(output, str):
            # Try to parse as JSON
            import json
            data = json.loads(output)
            return data.get('action') == 'research'
    except Exception as e:
        print(f"Error in is_research: {e}")
    return False

def is_reminder(output) -> bool:
    # Handle different types of output
    try:
        if hasattr(output, 'json'):
            if isinstance(output.json, dict):
                return output.json.get('action') == 'reminder'
            elif isinstance(output.json, str):
                import json
                data = json.loads(output.json)
                return data.get('action') == 'reminder'
        elif hasattr(output, 'pydantic') and output.pydantic:
            return getattr(output.pydantic, 'action', '') == 'reminder'
        elif isinstance(output, dict):
            return output.get('action') == 'reminder'
        elif isinstance(output, str):
            # Try to parse as JSON
            import json
            data = json.loads(output)
            return data.get('action') == 'reminder'
    except Exception as e:
        print(f"Error in is_reminder: {e}")
    return False

# Load configurations
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Get the absolute path of the configuration files
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

try:
    agents_config = load_config(os.path.join(root_dir, 'config', 'agents.yml'))
    tasks_config = load_config(os.path.join(root_dir, 'config', 'tasks.yml'))
except Exception as e:
    print(f"Error loading configuration: {e}")
    agents_config = {}
    tasks_config = {}

@CrewBase
class PostScreenshotCrew():
    """
        This crew will trigger after the user posts a screenshot and will execute any task specified by the user or just summarize the notes and the screenshot
    """
    
    def __init__(self):
        self.config = {}
        self.config.update(agents_config)
        self.config.update(tasks_config)
    
    @agent
    def task_classifier_agent(self,) -> Agent:
        return Agent(
            config=self.config['task_classifier_agent'],
            verbose=True,
            multimodal=True,
        )

    @agent
    def action_classifier_agent(self) -> Agent:
        return Agent(
            config=self.config['action_classifier_agent'],
            verbose=True,
        )

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.config['research_agent'],
            verbose=True,
            multimodal=True,
            tools=[web_search_tool],
            allow_delegation=True
        )

    @agent
    def reminder_agent(self) -> Agent:
        return Agent(
            config=self.config['reminder_agent'],
            verbose=True,
            tools=[reminder_tool]
        )

    @agent
    def summarize_notes_agent(self) -> Agent:
        return Agent(
            config=self.config['summarize_notes_agent'],
            verbose=True,
        )

    @task
    def task_classification_task(self) -> Task:
        return Task(
            config=self.config['task_classification_task'],
            agent=self.task_classifier_agent(),
            output_json=TaskClassificationOutput
        )

    @task
    def summarize_notes_task(self) -> Task:
        return Task(
            config=self.config['summarize_notes_task'],
            agent=self.summarize_notes_agent(),
            output_json=SummarizeNotesOutput
        )

    @task
    def action_classification_task(self) -> Task:
        return Task(
            config=self.config['action_classification_task'],
            agent=self.action_classifier_agent(),
            output_json=ActionClassificationOutput
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.config['research_task'],
            agent=self.research_agent(),
            output_file='research_output.md',
            tools=[web_search_tool],
            async_execution=True
        )

    @task
    def reminder_task(self) -> Task:
        return Task(
            config=self.config['reminder_task'],
            agent=self.reminder_agent(),
            tools=[reminder_tool]  # We'll use the tool directly and update params during execution
        )

    @crew
    def crew(self) -> Crew:
        # Add some debug prints to help diagnose issues with our config
        print("Loading Crew configuration...")
        
        # Create conditional tasks for task type classification
        task_type_conditional = ConditionalTask(
            description="Execute the summarize_notes_task if the classification is 'Summarize notes'",
            expected_output="A summary of the notes from the screenshot",
            condition=is_summary,
            agent=self.summarize_notes_agent()
        )
        
        # Create conditional task for action type
        action_type_conditional = ConditionalTask(
            description="Execute the research_task if the action type is 'research'",
            expected_output="Research results based on the screenshot",
            condition=is_research,
            agent=self.research_agent()
        )
        
        # Create conditional task for reminder
        reminder_conditional = ConditionalTask(
            description="Execute the reminder_task if the action type is 'reminder'",
            expected_output="Set a reminder for the user",
            condition=is_reminder,
            agent=self.reminder_agent()
        )
        
        print("Building Crew with tasks...")
        
        return Crew(
            agents=[
                self.task_classifier_agent(),
                self.summarize_notes_agent(),
                self.action_classifier_agent(),
                self.research_agent(),
                self.reminder_agent()
            ],
            tasks=[
                self.task_classification_task(),
                task_type_conditional,
                self.action_classification_task(),
                action_type_conditional,
                reminder_conditional
            ],
            verbose=True,
            process=Process.sequential
        )
