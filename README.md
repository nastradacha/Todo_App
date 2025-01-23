# Todo List Application with ChatGPT Integration

A PyQt6-based todo list app with AI task generation using OpenAI's API.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/nastradacha/Todo_App.git
   cd Todo_App
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Environment Setup:
   1. Create .env file in the project root: 
      . '''bash 
      touch .env
   2. Add your OpenAI API key to file: OPENAI_API_KEY=your-api-key-here
   3. The app will automatically:
         . Create the database (todo_app.db) on first run
         . Generate necessary tables

## Running the Application

1. '''Bash
   python todo_app.py


## Features

. Tabbed task organization

. ChatGPT task generation

. SQLite database storage

. Mark tasks as done/undone

. delete task or tabs