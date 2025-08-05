#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from grpc_load_tester import GrpcLoadTester

def main():
    # Test parameters
    target = "newibankdevcorp.kicb.net:443"
    
    # Request data
    data = {
        "username": "01229",
        "password": "password1"
    }
    
    # Metadata (lowercase keys for gRPC)
    metadata = {
        "refid": "9345712638845621",
        "device-type": "ios", 
        "user-agent": "12_MACBOOKDANDAN"
    }
    
    # Create tester for load testing
    tester = GrpcLoadTester(
        target=target,
        concurrency=5,           # 5 потоков  
        connections=5,           # 5 соединений
        total=100,              # 100 запросов
        timeout=30.0,           # увеличили таймаут
        rps=10,                 # 10 запросов в секунду
        keepalive=3.0
    )
    
    print("Running simple gRPC test...")
    print(f"Target: {target}")
    print(f"Data: {data}")
    print(f"Metadata: {metadata}")
    print("-" * 50)
    
    # Run test
    try:
        report = tester.run_test(data=data, metadata=metadata)
        tester.print_report(report)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 