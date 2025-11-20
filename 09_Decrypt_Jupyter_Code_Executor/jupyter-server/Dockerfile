# Dockerfile.jupyter
FROM python:3.13-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip install --no-cache-dir jupyter_kernel_gateway ipykernel numpy pandas sympy scipy --upgrade

RUN pip install --no-cache-dir -r requirements.txt --upgrade

EXPOSE 8888

ENV TOKEN="UNSET"
CMD python -m jupyter kernelgateway \
    --KernelGatewayApp.ip=0.0.0.0 \
    --KernelGatewayApp.port=8888 \
    --KernelGatewayApp.auth_token="${TOKEN}" \
    --JupyterApp.answer_yes=true \
    --JupyterWebsocketPersonality.list_kernels=true \
    --MappingKernelManager.cull_idle_timeout=1800 \
    --MappingKernelManager.cull_interval=300 \
    --MappingKernelManager.cull_connected=False \
    --MappingKernelManager.cull_busy=False \