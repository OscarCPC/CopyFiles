# CopyFiles

A PyQt5-based desktop application for efficient file management and content searching.

## Features

### File Operations
- Batch copy files and directories
- Multi-threaded file operations
- Progress tracking
- Directory cleanup utility
- Operation logging

### Search Capabilities
- Advanced text search within files
- Multiple logical operators:
  - AND: All patterns must match
  - OR: Any pattern can match
  - NOT: No patterns should match
  - XOR: Exactly one pattern should match
  - NAND: Not all patterns should match
  - NOR: None of the patterns should match
- Multi-threaded search operations
- Configurable thread count

## Project Structure

```
CopyFiles/
├── Copyfiles.py        # Main application file
├── Combinear.qss      # Style sheet file
├── README.md
└── anon/
    └── files/
        ├── found/     # Directory for search results
        └── log/       # Operation logs directory
            └── copyfiles.log
```

## Requirements

- Python 3.x
- PyQt5

## Installation

```bash
# Clone the repository
git clone https://github.com/OscarCPC/CopyFiles.git

# Install dependencies
pip install PyQt5
```

## Usage

### Starting the Application

```bash
python Copyfiles.py
```

### Modes

1. **Copy Files Mode**
   - Enter file/directory paths in the input area
   - Set number of threads (default: 4)
   - Click "Copiar" to start copying
   - Monitor progress in real-time

2. **Search Mode**
   - Enter search patterns
   - Select logical operator (AND, OR, NOT, XOR, NAND, NOR)
   - Configure search parameters
   - Results are moved to the 'found' directory

### Buttons

- **Copiar**: Start copy operation
- **Vaciar Destino**: Empty destination directory
- **Ver Log**: View operation logs
- **Abrir Destino**: Open destination folder

### Thread Configuration
- Default: 4 threads
- Adjustable via input field
- Higher thread count recommended for large operations

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Your License Here]

[Oscar González]


## Changelog

### Version 1.0.0
- Initial release
- Basic file copy functionality
- Multi-threaded operations
- Search capabilities with logical operators

## Future Enhancements
- [ ] File filtering by extension
- [ ] Improved error handling
- [ ] Advanced search patterns
- [ ] Custom destination folders
- [ ] Operation queuing

## Support
For support, please open an issue in the GitHub repository.

## Acknowledgments
- PyQt5 team
- [Other acknowledgments]
