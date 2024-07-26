# Use the official Python 3.12 slim image as the base image
FROM python:3.12-slim

# Add image metadata
LABEL org.opencontainers.image.authors="Courageous Comets ☄️"
LABEL org.opencontainers.image.description="This application was built by the Courageous Comets team for the Python Discord Summer Code Jam 2024"
LABEL org.opencontainers.image.documentation=https://thijsfranck.github.io/courageous-comets/
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.source=https://github.com/thijsfranck/courageous-comets
LABEL org.opencontainers.image.title="Courageous Comets"

# Set default environment variables
ENV BOT_CONFIG_PATH=/app/application.yaml
ENV LOG_LEVEL=INFO
ENV MPLCONFIGDIR=/app/matplotlib
ENV NLTK_DATA=/app/nltk_data
ENV HF_HOME=/app/hf_data

# Add a non-root user and group
RUN addgroup --system courageous-comets && \
    adduser --system --ingroup courageous-comets courageous-comets

# Set the working directory
WORKDIR /app

# Assign the working directory to the non-root user and set the permissions
RUN chown -R courageous-comets:courageous-comets /app && \
    chmod -R 0770 /app

# Copy the app config and the wheel file to the working directory and set the permissions
COPY --chown=courageous-comets:courageous-comets --chmod=0440 application.yaml dist/*.whl ./

# Install the wheel file and clean up to reduce image size
RUN pip install --no-cache-dir *.whl && \
    rm *.whl

# Switch to the non-root user
USER courageous-comets

# Run the application
ENTRYPOINT ["python", "-m", "courageous_comets"]
