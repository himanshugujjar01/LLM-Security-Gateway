import asyncio
import time
import statistics
import httpx


API_URL = "http://127.0.0.1:8000/chat"
API_KEY = "my-secret-key"

TOTAL_REQUESTS = 20
CONCURRENT_REQUESTS = 5


async def send_request(client, request_id):
    payload = {
        "message": f"Latency test request number {request_id}"
    }

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    start_time = time.perf_counter()

    try:
        response = await client.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        end_time = time.perf_counter()
        latency = end_time - start_time

        return {
            "request_id": request_id,
            "status_code": response.status_code,
            "latency": latency,
            "success": response.status_code == 200
        }

    except Exception as error:
        end_time = time.perf_counter()
        latency = end_time - start_time

        return {
            "request_id": request_id,
            "status_code": "ERROR",
            "latency": latency,
            "success": False,
            "error": str(error)
        }


async def run_stress_test():
    print("\nStarting LLM Security Gateway Stress Test...\n")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Concurrent Requests: {CONCURRENT_REQUESTS}")
    print(f"Target URL: {API_URL}\n")

    results = []

    async with httpx.AsyncClient() as client:
        for batch_start in range(0, TOTAL_REQUESTS, CONCURRENT_REQUESTS):
            tasks = []

            for i in range(batch_start, min(batch_start + CONCURRENT_REQUESTS, TOTAL_REQUESTS)):
                tasks.append(
                    send_request(client, i + 1)
                )

            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            # Small delay to avoid rate limiter blocking everything
            await asyncio.sleep(1)

    latencies = [result["latency"] for result in results]
    successful_requests = len([r for r in results if r["success"]])
    failed_requests = TOTAL_REQUESTS - successful_requests

    status_codes = {}

    for result in results:
        code = result["status_code"]
        status_codes[code] = status_codes.get(code, 0) + 1

    print("\nStress Test Completed")
    print("----------------------------------")
    print(f"Total Requests Sent: {TOTAL_REQUESTS}")
    print(f"Successful Requests: {successful_requests}")
    print(f"Failed / Blocked Requests: {failed_requests}")
    print(f"Status Code Summary: {status_codes}")
    print("----------------------------------")
    print(f"Average Latency: {statistics.mean(latencies):.4f} seconds")
    print(f"Minimum Latency: {min(latencies):.4f} seconds")
    print(f"Maximum Latency: {max(latencies):.4f} seconds")

    if len(latencies) > 1:
        print(f"Median Latency: {statistics.median(latencies):.4f} seconds")

    print("----------------------------------\n")


if __name__ == "__main__":
    asyncio.run(run_stress_test())