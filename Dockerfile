# Use the latest Python slim image for our base environment
FROM python:3.12-slim as base

# Set environment variables to disable Python bytecode generation and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory for the app inside the container
WORKDIR /app

# Add a non-privileged user for running the app
# This is a security measure to avoid running the app as root
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install dependencies from the requirements.txt file
# Using a cache mount to speed up the build process and avoid reinstalling dependencies each time
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt

# Switch to the non-root user to run the application (this enhances security)
USER appuser

# Copy the entire project into the container
COPY . .

# Expose port 5000 as Flask app by default runs on this port
EXPOSE 5000

# Start the Flask app in development mode with auto-reload enabled for easy updates during development
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]
