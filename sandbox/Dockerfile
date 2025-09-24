FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
# Install SSH + FTP + nmap + nano + ss + enum4linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd ca-certificates netcat-openbsd nmap nano iproute2 samba && \
    rm -rf /var/lib/apt/lists/*

# Create a test user (lab-only credentials)
RUN useradd -m -s /bin/bash testuser && echo 'testuser:testpass' | chpasswd

# SSH setup
RUN mkdir -p /var/run/sshd && \
    sed -i 's@session\\s*required\\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd

# FTP setup dirs
RUN mkdir -p /var/run/vsftpd/empty /home/testuser/ftp && \
    chown -R testuser:testuser /home/testuser

# Add vsftpd config
COPY vsftpd.conf /etc/vsftpd.conf

# Expose SSH, FTP, and passive FTP ports
EXPOSE 22 21 30000-30009

# Keep services in foreground
CMD ["bash"]