# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Update package list and install reconnaissance tools
RUN apt-get update && apt-get install -y \
    nmap \
    dnsutils \
    whois \
    netcat-traditional \
    curl \
    wget \
    git \
    traceroute \
    iputils-ping \
    telnet \
    masscan \
    nikto \
    dirb \
    gobuster \
    whatweb \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY server.py .

# Make server.py executable
RUN chmod +x server.py

# Expose any port if needed (though MCP uses stdio)
# EXPOSE 8000

# Set the default command to run the MCP server
CMD ["python", "server.py"]