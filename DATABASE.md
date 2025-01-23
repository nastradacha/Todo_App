
### **2. Create DATABASE.md**
Create a new file named `DATABASE.md` with database-specific info:

```markdown
# Database Configuration

## Schema Overview
The application uses SQLite with two tables:

### `tabs` Table
| Column | Type    | Description          |
|--------|---------|----------------------|
| id     | INTEGER | Primary key          |
| name   | TEXT    | Unique tab name      |

### `tasks` Table
| Column       | Type    | Description                     |
|--------------|---------|---------------------------------|
| id           | INTEGER | Primary key                     |
| tab_name     | TEXT    | Associated tab name             |
| description  | TEXT    | Task description                |
| done         | BOOLEAN | Completion status (0/1)         |

## Management
- The database (`todo_app.db`) is auto-created on first run
- **Do NOT manually edit the .db file** - use the application interface
- Located in the project root directory

## Backup
To backup your tasks:
1. Copy `todo_app.db` to safe location
2. Restore by replacing the file