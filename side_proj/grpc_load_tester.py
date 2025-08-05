#!/usr/bin/env python3

import asyncio
import argparse
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
import statistics
from datetime import datetime
import sys
import os

# Add current directory to path to import protobuf modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import grpc
    from grpc import ssl_channel_credentials
except ImportError:
    print("grpcio not installed. Install with: pip install grpcio grpcio-tools")
    sys.exit(1)

# Try to import protobuf generated modules
try:
    import protofile_pb2
    import protofile_pb2_grpc
except ImportError:
    print("Protobuf modules not found. Generate them using:")
    print("python -m grpc_tools.protoc --python_out=. --grpc_python_out=. protofile.proto")
    sys.exit(1)


class GrpcLoadTester:
    def __init__(self, target: str, concurrency: int = 1, connections: int = 1, 
                 total: int = 10, timeout: float = 20.0, rps: Optional[int] = None,
                 keepalive: float = 3.0):
        self.target = target
        self.concurrency = concurrency
        self.connections = connections
        self.total = total
        self.timeout = timeout
        self.rps = rps
        self.keepalive = keepalive
        self.results = []
        self.lock = threading.Lock()
    
    def create_channel(self) -> grpc.Channel:
        """Create gRPC channel with SSL and keepalive"""
        options = [
            ('grpc.keepalive_time_ms', int(self.keepalive * 1000)),
            ('grpc.keepalive_timeout_ms', 10000),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.max_receive_message_length', -1),
            ('grpc.max_send_message_length', -1),
        ]
        
        # Use SSL for port 443
        if self.target.endswith(':443'):
            credentials = ssl_channel_credentials()
            return grpc.secure_channel(self.target, credentials, options=options)
        else:
            return grpc.insecure_channel(self.target, options=options)
    
    def create_metadata(self, metadata_dict: Dict[str, str]) -> List[tuple]:
        """Convert metadata dictionary to gRPC metadata format"""
        return [(key, value) for key, value in metadata_dict.items()]
    
    def single_request(self, data: Dict, metadata: Dict[str, str]) -> Dict:
        """Perform a single gRPC request"""
        start_time = time.time()
        result = {
            'success': False,
            'duration': 0.0,
            'error': None,
            'response': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with self.create_channel() as channel:
                stub = protofile_pb2_grpc.WebAuthApiStub(channel)
                
                # Create request
                request = protofile_pb2.LoginRequest(
                    username=data.get('username', ''),
                    password=data.get('password', '')
                )
                
                # Create metadata
                grpc_metadata = self.create_metadata(metadata)
                
                # Make the call
                response = stub.authenticate(
                    request,
                    metadata=grpc_metadata,
                    timeout=self.timeout
                )
                
                result['success'] = True
                result['response'] = {
                    'success': response.success,
                    'sessionKey': response.data.sessionKey if response.data else None,
                    'sessionId': response.data.sessionId if response.data else None,
                    'otpDelivery': response.data.otpDelivery if response.data else None,
                    'state': response.data.state if response.data else None,
                    'error_code': response.error.code if response.error else None,
                    'error_data': response.error.data if response.error else None
                }
                
        except grpc.RpcError as e:
            result['error'] = f"gRPC Error: {e.code().name} - {e.details()}"
        except Exception as e:
            result['error'] = f"Error: {str(e)}"
        finally:
            result['duration'] = time.time() - start_time
            
        return result
    
    def worker_thread(self, data: Dict, metadata: Dict[str, str], request_count: int) -> List[Dict]:
        """Worker thread to perform multiple requests with optional RPS limiting"""
        results = []
        
        # Calculate delay between requests if RPS is specified
        delay = 0.0
        if self.rps:
            delay = 1.0 / self.rps
        
        for i in range(request_count):
            if i > 0 and delay > 0:
                time.sleep(delay)
                
            result = self.single_request(data, metadata)
            results.append(result)
            
            with self.lock:
                self.results.append(result)
                
        return results
    
    def run_test(self, data: Dict, metadata: Dict[str, str]) -> Dict:
        """Run load test with specified parameters"""
        
        print(f"Starting gRPC load test...")
        print(f"Target: {self.target}")
        print(f"Concurrency: {self.concurrency}")
        print(f"Connections: {self.connections}")
        print(f"Total requests: {self.total}")
        print(f"Timeout: {self.timeout}s")
        if self.rps:
            print(f"RPS: {self.rps}")
        print(f"Keepalive: {self.keepalive}s")
        print("-" * 50)
        
        self.results = []
        start_time = time.time()
        
        # Calculate requests per thread
        requests_per_thread = self.total // self.concurrency
        remaining_requests = self.total % self.concurrency
        
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            futures = []
            for i in range(self.concurrency):
                thread_requests = requests_per_thread + (1 if i < remaining_requests else 0)
                future = executor.submit(
                    self.worker_thread, 
                    data, metadata, thread_requests
                )
                futures.append(future)
            
            # Wait for all threads to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Worker thread error: {e}")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        return self.generate_report(total_duration)
    
    def generate_report(self, total_duration: float) -> Dict:
        """Generate test report"""
        if not self.results:
            return {"error": "No results to report"}
        
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]
        
        durations = [r['duration'] for r in successful_requests]
        
        report = {
            'total_requests': len(self.results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(self.results) * 100,
            'total_duration': total_duration,
            'requests_per_second': len(self.results) / total_duration,
            'successful_rps': len(successful_requests) / total_duration,
        }
        
        if durations:
            report.update({
                'avg_response_time': statistics.mean(durations),
                'min_response_time': min(durations),
                'max_response_time': max(durations),
                'median_response_time': statistics.median(durations),
                'p95_response_time': self.percentile(durations, 95),
                'p99_response_time': self.percentile(durations, 99),
            })
        
        return report
    
    def percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def print_report(self, report: Dict):
        """Print report in pretty format"""
        print("\n" + "="*50)
        print("gRPC LOAD TEST RESULTS")
        print("="*50)
        print(f"Total requests:      {report['total_requests']}")
        print(f"Successful requests: {report['successful_requests']}")
        print(f"Failed requests:     {report['failed_requests']}")
        print(f"Success rate:        {report['success_rate']:.2f}%")
        print(f"Total duration:      {report['total_duration']:.2f}s")
        print(f"Requests per second: {report['requests_per_second']:.2f}")
        print(f"Successful RPS:      {report['successful_rps']:.2f}")
        
        if 'avg_response_time' in report:
            print(f"\nResponse times:")
            print(f"  Average:    {report['avg_response_time']*1000:.2f}ms")
            print(f"  Min:        {report['min_response_time']*1000:.2f}ms")
            print(f"  Max:        {report['max_response_time']*1000:.2f}ms")
            print(f"  Median:     {report['median_response_time']*1000:.2f}ms")
            print(f"  95th perc:  {report['p95_response_time']*1000:.2f}ms")
            print(f"  99th perc:  {report['p99_response_time']*1000:.2f}ms")
        
        # Show some failed requests if any
        failed_requests = [r for r in self.results if not r['success']]
        if failed_requests:
            print(f"\nSample errors:")
            for i, error in enumerate(failed_requests[:5]):
                print(f"  {i+1}. {error['error']}")
        
        print("="*50)


def main():
    parser = argparse.ArgumentParser(description='gRPC Load Tester (ghz-style)')
    
    # ghz compatible parameters
    parser.add_argument('target', help='Target gRPC server (host:port)')
    parser.add_argument('--concurrency', type=int, default=1, help='Number of concurrent workers')
    parser.add_argument('--connections', type=int, default=1, help='Number of connections to keep open')
    parser.add_argument('--total', type=int, default=10, help='Total number of requests')
    parser.add_argument('--timeout', default='20s', help='Request timeout (e.g., 20s)')
    parser.add_argument('--rps', type=int, help='Rate limit in requests per second')
    parser.add_argument('--keepalive', default='3s', help='Keepalive time (e.g., 3s)')
    
    # Protocol and call specification
    parser.add_argument('--proto', required=True, help='Protocol buffer file')
    parser.add_argument('--call', required=True, help='gRPC method to call')
    
    # Data and metadata
    parser.add_argument('-d', '--data', required=True, help='Request data as JSON string')
    parser.add_argument('-m', '--metadata', help='Request metadata as JSON string')
    
    # Output format
    parser.add_argument('--format', default='pretty', choices=['pretty', 'json'], help='Output format')
    
    args = parser.parse_args()
    
    # Parse timeout
    timeout_str = args.timeout.lower()
    if timeout_str.endswith('s'):
        timeout = float(timeout_str[:-1])
    elif timeout_str.endswith('ms'):
        timeout = float(timeout_str[:-2]) / 1000
    else:
        timeout = float(timeout_str)
    
    # Parse keepalive
    keepalive_str = args.keepalive.lower()
    if keepalive_str.endswith('s'):
        keepalive = float(keepalive_str[:-1])
    elif keepalive_str.endswith('ms'):
        keepalive = float(keepalive_str[:-2]) / 1000
    else:
        keepalive = float(keepalive_str)
    
    # Parse data and metadata
    try:
        data = json.loads(args.data)
        metadata = json.loads(args.metadata) if args.metadata else {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return 1
    
    # Create tester
    tester = GrpcLoadTester(
        target=args.target,
        concurrency=args.concurrency,
        connections=args.connections,
        total=args.total,
        timeout=timeout,
        rps=args.rps,
        keepalive=keepalive
    )
    
    # Run test
    try:
        report = tester.run_test(data=data, metadata=metadata)
        
        if args.format == 'pretty':
            tester.print_report(report)
        else:
            print(json.dumps(report, indent=2))
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"Error during test: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 