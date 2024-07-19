# Use the official Python 3.12 slim image as the base image
FROM python:3.12-slim

# Add image metadata
LABEL org.opencontainers.image.authors="Courageous Comets ☄️"
LABEL org.opencontainers.image.description="This application was built by the Courageous Comets team for the Python Discord Summer Code Jam 2024"
LABEL org.opencontainers.image.documentation=https://thijsfranck.github.io/courageous-comets/
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.source=https://github.com/thijsfranck/courageous-comets
LABEL org.opencontainers.image.title="Courageous Comets"

# Add a non-root user
RUN adduser --system courageous-comets

# Set the working directory
WORKDIR /app

# Copy the wheel file to the working directory
COPY dist/*.whl ./

# Install the wheel file and clean up to reduce image size
RUN pip install --no-cache-dir *.whl && \
    rm *.whl

# Switch to the non-root user
USER courageous-comets

# Run the application
ENTRYPOINT ["python", "-m", "courageous_comets"]
