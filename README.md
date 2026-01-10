# Auto Shutdown System

A modern Windows application for scheduling automatic system shutdowns with an elegant GUI interface.

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **Modern UI** - Clean, mobile-inspired design with rounded corners and smooth animations
- **Flexible Scheduling** - Set shutdown time with 12/24-hour format support
- **Weekly Repeat** - Select specific days of the week for recurring shutdowns
- **Visual Feedback** - Animated time display with blinking colon
- **Persistent Settings** - Configuration auto-saves and persists across reboots
- **1-Minute Warning** - System displays a warning before shutdown

## Screenshots

The application features a modern card-based UI design:

- Large time display with interactive hour/minute selection
- Pill-style toggle for 12/24-hour format
- Circular day-of-week selector buttons
- Collapsible help section
- Status indicator showing current schedule state

## Requirements

- Windows 10/11
- Python 3.6 or higher (recommended 3.8+)
- Administrator privileges (for creating scheduled tasks)
- No external dependencies required (uses only Python standard library)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/auto-shutdown.git
cd auto-shutdown
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python main.py
```

Or run with administrator privileges (recommended):
```bash
# Right-click run_as_admin.bat and select "Run as administrator"
```

### Setting Up a Shutdown Schedule

1. **Select Time** - Click on the hour or minute display to choose your desired shutdown time
2. **Choose Format** - Toggle between 24-hour and 12-hour format using the pill switch
3. **Select Days** - Click on the circular day buttons to select which days to run (click "Select All" to toggle all days)
4. **Enable Repeat** - Toggle the repeat switch to run the schedule weekly
5. **Apply** - Click "Set Shutdown" to create the schedule

### Managing Schedules

- **Cancel Shutdown** - Remove the current scheduled shutdown
- **Check Schedule** - View details of the active shutdown schedule

## Project Structure

```
auto-shutdown/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── run_as_admin.bat       # Windows admin launcher
├── src/
│   ├── __init__.py
│   ├── scheduler.py       # Windows Task Scheduler integration
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py    # Main application window
│       ├── modern_theme.py   # Colors and fonts configuration
│       └── modern_widgets.py # Custom UI components
└── spec/
    ├── screen.png         # UI design reference
    └── code.html          # Design specification
```

## Configuration

Settings are automatically saved to `~/.auto_shutdown_config.json` and include:

- Selected weekdays
- Shutdown time
- Repeat mode preference
- Time format (12/24-hour)

## Technical Details

### Windows Task Scheduler Integration

The application uses Windows Task Scheduler (`schtasks`) to create persistent shutdown tasks that:

- Run with SYSTEM privileges
- Execute `shutdown /s /t 60` (60-second warning)
- Persist across system reboots

### UI Framework

Built with Python's tkinter library featuring:

- Custom canvas-based widgets for modern styling
- Rounded corners using arc drawing
- Animated elements (blinking colon)
- Responsive button hover/press states

## Troubleshooting

### "Access Denied" Error
Run the application as administrator to create scheduled tasks.

### Schedule Not Working
1. Check Windows Task Scheduler for the task named "AutomaticShutdownScheduler"
2. Verify the task is enabled and has correct trigger settings
3. Ensure no other software is blocking scheduled tasks

### Font Display Issues
The application uses "Microsoft JhengHei UI" font. If text appears incorrectly, ensure this font is installed on your system.

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
