FROM python:3.11-slim-bullseye

RUN mkdir /app
WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8585
CMD ["streamlit", "run", "--server.port", "8585", "./streamlit_app.py"]