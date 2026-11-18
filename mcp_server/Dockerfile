FROM python:3.12-slim
WORKDIR /service
COPY mcp_server/requirements.lock.txt /service/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY mcp_server /service/mcp_server
EXPOSE 8001
CMD ["python", "-m", "mcp_server.server", "--transport", "http", "--host", "0.0.0.0", "--port", "8001"]
