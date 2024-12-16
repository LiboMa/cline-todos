# Use Python 3 base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY backend/ backend/
COPY static/ static/
COPY run.py .

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV SECRET_KEY=change-this-in-production
ENV JWT_SECRET_KEY=change-this-in-production

# Create volume for SQLite database
VOLUME ["/app/backend"]

# Expose the port the app runs on
EXPOSE 5001

# Run the application
CMD ["python", "run.py"]
