# Custom Docker image for n8n with Python dependencies pre-installed

FROM n8nio/n8n:latest

USER root

# Install Python and pip
RUN apk add --no-cache \
    python3 \
    python3-dev \
    py3-pip \
    build-base \
    libffi-dev \
    openssl-dev

# Install Python packages needed for Code nodes
RUN pip3 install --no-cache-dir \
    PyMuPDF==1.23.8 \
    langchain==0.1.0 \
    langchain-text-splitters==0.0.1 \
    genanki==0.13.0

# Switch back to node user
USER node

# Set environment to allow external packages
ENV NODE_FUNCTION_ALLOW_EXTERNAL=PyMuPDF,langchain,langchain-text-splitters,genanki
ENV NODE_FUNCTION_ALLOW_BUILTIN=*

# Expose n8n port
EXPOSE 5678

# Start n8n
CMD ["n8n"]
