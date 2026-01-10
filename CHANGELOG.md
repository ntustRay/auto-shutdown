# Auto Shutdown System - Change Log

## [v1.0.1] - 2026-01-11

### 🔧 Improvements
- **Cross-platform font support**: Added fallback font system for better compatibility
- **Code refactoring**: Split large functions into smaller, more maintainable components
- **Enhanced error handling**: Better user feedback for different error types
- **Dependency cleanup**: Now uses only Python standard library

### 🛠️ Technical Changes
- **Font System**: Implemented `get_font_fallback()` and `get_safe_font()` functions
- **Modular Design**: Refactored `_show_number_picker()` into 6 focused helper functions
- **Error Handling**: Added specific error handlers for validation, permission, and general errors
- **Parameter Cleanup**: Removed unused `_is_repeat` parameter from scheduler

### 📦 Dependencies
- Removed unused `schedule` library requirement
- Now uses only Python standard library modules

### 🐛 Bug Fixes
- Fixed requirements.txt syntax error
- Improved font rendering compatibility across systems
- Better error messages for permission issues

### 📚 Documentation
- Updated README with corrected requirements information
- Added detailed function documentation
- Improved inline comments throughout codebase

---

## [v1.0.0] - 2026-01-09
- Initial Release
- Basic auto shutdown functionality
- Modern UI with tkinter
- Windows Task Scheduler integration
- Weekly scheduling support
- 12/24 hour format toggle
