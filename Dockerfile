FROM python:3.11
WORKDIR /usr/src/app

COPY . .
RUN python -m pip install --no-cache-dir -r run.requirements.txt

CMD [ "python", "-m", "market" ]