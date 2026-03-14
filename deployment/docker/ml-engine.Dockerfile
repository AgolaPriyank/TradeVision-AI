FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

# Install heavy data science dependencies
RUN pip install --no-cache-dir numpy pandas scikit-learn
RUN pip install --no-cache-dir torch xgboost
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "prediction_api.main:app", "--host", "0.0.0.0", "--port", "8001"]
