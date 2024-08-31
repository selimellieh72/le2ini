# Step 1: Use an official Python runtime as a parent image
FROM python:3.10

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Step 4: Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the current directory contents into the container at /app
COPY . /app/

# Step 6: Expose the port the app runs on
EXPOSE 8000

# Step 7: Define environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Step 8: Run the command to start the app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
