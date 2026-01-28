import uvicorn

if __name__ == "__main__":
        uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=7003,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )