FROM python:3.12-slim
WORKDIR /service
COPY mcp_server/requirements.lock.txt /service/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY mcp_server /service/mcp_server
COPY agent_server /service/agent_server
EXPOSE 8002
CMD ["python", "-m", "agent_server.server", "--host", "0.0.0.0", "--port", "8002"]
