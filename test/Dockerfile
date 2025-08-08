FROM python:3.10
RUN apt-get update && apt-get install -y curl
WORKDIR /app
COPY naive_image/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY naive_image/app/ ./app/
COPY naive_image/sample_data/ ./sample_data/
RUN echo "Build complete" > /app/build_status.txt
# Command to run the application when the container starts.
CMD ["python", "app/predictor.py", "sample_data/sample_text.txt"]