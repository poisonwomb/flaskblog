# Pull official base image
FROM python:3.11.6-bookworm

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Print environment variables
RUN printenv

# Install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv
COPY Pipfile Pipfile.lock /usr/src/app/
RUN pipenv install --deploy --ignore-pipfile
COPY . /usr/src/app

EXPOSE 5000

CMD ["pipenv", "run", "python", "-u", "run.py"]