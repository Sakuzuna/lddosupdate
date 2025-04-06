import asyncio
import aiohttp
import logging
import time
from aiohttp_socks import ProxyConnector, ProxyType
import socket
import random
from typing import List
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proxy_check.log'),
        logging.StreamHandler()
    ]
)

TEST_URLS = [
    'http://www.google.com',
    'http://www.cloudflare.com',
    'http://www.github.com'
]

def is_valid_socks5_format(proxy_info: str) -> bool:
    """Basic format check for proxy (ip:port)"""
    try:
        ip, port = proxy_info.split(':')
        port = int(port)
        socket.inet_aton(ip)
        return 0 <= port <= 65535
    except (ValueError, socket.error):
        return False

async def check_proxy(
    proxy_info: str,
    session: aiohttp.ClientSession,
    test_url: str,
    timeout: aiohttp.ClientTimeout
) -> bool:
    """Check if a proxy is working and supports SOCKS5"""
    try:
        async with session.get(test_url, timeout=timeout) as response:
            if response.status == 200:
                return True
            return False
    except (aiohttp.ClientError, asyncio.TimeoutError, OSError):
        return False

async def process_proxy(
    proxy_info: str,
    semaphore: asyncio.Semaphore,
    valid_proxies: List[str],
    timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=5)
) -> None:
    """Process a single proxy with multiple checks"""
    async with semaphore:
        if not is_valid_socks5_format(proxy_info):
            logging.warning(f"Proxy {proxy_info} - SKIPPED: Invalid format")
            return

        proxy_url = f"socks5://{proxy_info}"
        connector = ProxyConnector(
            proxy_type=ProxyType.SOCKS5,
            host=proxy_info.split(':')[0],
            port=int(proxy_info.split(':')[1]),
            verify_ssl=False,
            limit_per_host=1
        )

        test_url = random.choice(TEST_URLS)
        
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                # Perform quick check first
                if not await check_proxy(proxy_info, session, test_url, timeout):
                    logging.warning(f"Proxy {proxy_info} - FAILED: Initial check")
                    return
                
                # Perform second verification
                test_url = random.choice(TEST_URLS)
                if not await check_proxy(proxy_info, session, test_url, timeout):
                    logging.warning(f"Proxy {proxy_info} - FAILED: Verification check")
                    return
                
                # If both checks passed, add to valid proxies
                valid_proxies.append(proxy_info)
                logging.info(f"Proxy {proxy_info} - SUCCESS: SOCKS5 confirmed")
                
        except Exception as e:
            logging.warning(f"Proxy {proxy_info} - FAILED: {str(e)}")

async def main():
    # Read proxies from file
    try:
        with open('proxy.txt', 'r') as f:
            proxies = list({line.strip() for line in f if line.strip()})  # Remove duplicates
    except FileNotFoundError:
        logging.error("proxy.txt not found!")
        return
    
    proxy_count = len(proxies)
    if proxy_count == 0:
        logging.error("No proxies found in proxy.txt!")
        return
    
    logging.info(f"Found {proxy_count} unique proxies to check")
    
    # Adjust these values based on your system capabilities
    max_concurrent = 500  # Increased from 200 for faster checking
    semaphore = asyncio.Semaphore(max_concurrent)
    valid_proxies = []
    
    # Create tasks for all proxies
    tasks = [
        process_proxy(proxy, semaphore, valid_proxies)
        for proxy in proxies
    ]
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks)
    
    # Save only working SOCKS5 proxies
    with open('checked.txt', 'w') as f:
        for proxy in valid_proxies:
            f.write(f"{proxy}\n")
    
    logging.info(f"Found {len(valid_proxies)} working SOCKS5 proxies out of {proxy_count}")
    logging.info("Results saved to checked.txt")

if __name__ == "__main__":
    # Required packages: pip install aiohttp aiohttp-socks
    try:
        import aiohttp
        import aiohttp_socks
    except ImportError:
        logging.error("Please install required packages: pip install aiohttp aiohttp-socks")
        exit(1)
    
    start_time = time.time()
    
    # Windows requires this event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the async main function
    asyncio.run(main())
    
    execution_time = time.time() - start_time
    logging.info(f"Completed in {execution_time:.2f} seconds")
