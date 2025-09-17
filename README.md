# Reconnaissance MCP Server

A modular MCP (Model Context Protocol) server built with FastMCP for running reconnaissance and footprinting tasks in a secure, containerized environment.

## 🚀 Features

- **MCP-compliant server** using FastMCP framework
- **Single unified interface** (`run_tool`) for executing reconnaissance commands
- **Containerized deployment** with Docker for isolation and security
- **Pre-installed reconnaissance tools** including nmap, whois, dnsutils, and more
- **Portable and reusable** across different environments
- **Security-focused** with timeouts and proper error handling

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- Docker (recommended for deployment)
- Linux/macOS/Windows with WSL2

### Python Dependencies
```
fastmcp>=2.0.0
```

## 🛠️ Installation & Setup

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd reconMCP
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t recon-mcp .
   ```

3. **Run the container:**
   ```bash
   docker run -i recon-mcp
   ```

### Option 2: Local Development Setup

1. **Clone and navigate to the project:**
   ```bash
   git clone <your-repo-url>
   cd reconMCP
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   python server.py
   ```

## ⚙️ Configuration

### MCP Client Configuration

To use this server with Claude Desktop or other MCP clients, add the following to your MCP configuration:

#### For Claude Desktop (Linux/macOS):
Location: `~/.config/claude/mcp.json`

```json
{
  "servers": {
    "recon-server": {
      "command": "python",
      "args": ["/path/to/your/reconMCP/server.py"],
      "env": {}
    }
  }
}
```

#### For Claude Desktop (Windows):
Location: `%APPDATA%\Claude\mcp.json`

```json
{
  "servers": {
    "recon-server": {
      "command": "python",
      "args": ["C:\\path\\to\\your\\reconMCP\\server.py"],
      "env": {}
    }
  }
}
```

#### Using Docker with MCP Client:
```json
{
  "servers": {
    "recon-server": {
      "command": "docker",
      "args": ["run", "-i", "recon-mcp"],
      "env": {}
    }
  }
}
```

### Environment Variables

You can customize the server behavior with environment variables:

- `MCP_SERVER_NAME`: Server name (default: "recon-server")
- `TOOL_TIMEOUT`: Command timeout in seconds (default: 300)

## 🔧 Usage

### Available Tool

The server exposes a single MCP tool:

#### `run_tool`
Executes reconnaissance tools with specified arguments.

**Parameters:**
- `tool` (string): The command to run (e.g., 'nmap', 'dig', 'whois')
- `args` (list of strings): Arguments for the tool

**Returns:**
```json
{
  "stdout": "command output",
  "stderr": "error output if any",
  "returncode": 0,
  "command": "full command that was executed"
}
```

### Example Usage

#### Network Scanning
```json
{
  "tool": "nmap",
  "args": ["-sn", "192.168.1.0/24"]
}
```

#### DNS Lookup
```json
{
  "tool": "dig",
  "args": ["example.com", "A"]
}
```

#### Domain Information
```json
{
  "tool": "whois",
  "args": ["example.com"]
}
```

#### Web Technology Detection
```json
{
  "tool": "whatweb",
  "args": ["https://example.com"]
}
```

## 🛡️ Security Considerations

### Built-in Security Features
- **Command timeout**: 5-minute limit prevents hanging processes
- **Subprocess protection**: Uses list-based arguments to prevent shell injection
- **Container isolation**: Docker deployment isolates tools from host system
- **Error handling**: Graceful handling of missing tools and failed commands

### Important Security Notes
⚠️ **WARNING**: This tool is designed for authorized security testing only.

- Only use on networks and systems you own or have explicit permission to test
- Be aware of local laws and regulations regarding network scanning
- Consider using VPNs or isolated networks for testing
- Monitor and log all reconnaissance activities
- Some tools may trigger security alerts or be detected by monitoring systems

### Recommended Security Practices
- Run in isolated Docker containers
- Use dedicated testing networks
- Implement proper logging and monitoring
- Regular security updates of base images and tools
- Restrict network access where possible

## 📦 Available Reconnaissance Tools

The Docker container includes these pre-installed tools:

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| **nmap** | Network discovery and security auditing | Port scanning, service detection |
| **masscan** | Fast port scanner | Large-scale port scanning |
| **dig** | DNS lookup utility | DNS record queries |
| **whois** | Domain registration information | Domain ownership lookup |
| **curl/wget** | HTTP clients | Web requests and downloads |
| **netcat** | Network debugging | Port connectivity testing |
| **traceroute** | Network route tracing | Network path analysis |
| **nikto** | Web server scanner | Web vulnerability scanning |
| **dirb** | Web content scanner | Directory enumeration |
| **gobuster** | Directory/file/DNS busting | Fast directory discovery |
| **whatweb** | Web technology identifier | Technology stack detection |

## 🐛 Troubleshooting

### Common Issues

1. **Tool not found error:**
   - Ensure the tool is installed in your environment
   - Check if running in Docker with pre-installed tools

2. **Permission denied:**
   - Some tools require elevated privileges
   - Consider running Docker with appropriate permissions

3. **Timeout errors:**
   - Increase timeout value for long-running scans
   - Break large scans into smaller chunks

4. **MCP connection issues:**
   - Verify the path in your MCP configuration
   - Check that Python environment is accessible
   - Ensure all dependencies are installed

## 📝 Development

### Adding New Tools

To add new reconnaissance tools:

1. Install the tool in the Dockerfile
2. The `run_tool` function automatically supports any installed command
3. Update documentation with usage examples

### Testing

Test the server locally:
```bash
python server.py
```

Test with Docker:
```bash
docker build -t recon-mcp . && docker run -i recon-mcp
```

## 📄 License

This project is provided as-is for educational and authorized penetration testing purposes only. Users are responsible for compliance with applicable laws and regulations.

## ⚠️ Disclaimer

This tool is intended for authorized security professionals and researchers. Unauthorized access to computer networks is illegal. Always ensure you have proper authorization before conducting any reconnaissance activities.

## 🤝 Contributing

Contributions are welcome! Please ensure all contributions maintain the security-focused approach and include appropriate documentation.

## 📞 Support

For issues and questions, please open an issue in the GitHub repository.