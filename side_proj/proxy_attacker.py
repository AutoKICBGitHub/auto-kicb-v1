#!/usr/bin/env python3

import asyncio
import argparse
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
import statistics
from datetime import datetime, timedelta
import sys
import os
import random
import urllib.parse
import socket
import requests

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
    # You'll need to generate these using: python -m grpc_tools.protoc --python_out=. --grpc_python_out=. protofile.proto
    import protofile_pb2
    import protofile_pb2_grpc
except ImportError:
    print("Protobuf modules not found. Generate them using:")
    print("python -m grpc_tools.protoc --python_out=. --grpc_python_out=. protofile.proto")
    sys.exit(1)


class GrpcStressTester:
    def __init__(self, target: str, proto_file: str = "protofile.proto", insecure: bool = False, proxy_file: str = None, grpc_web: bool = False):
        self.target = target
        self.proto_file = proto_file
        self.insecure = insecure
        self.grpc_web = grpc_web
        self.results = []
        self.lock = threading.Lock()
        self.proxies = []
        self.current_proxy_index = 0
        self.proxy_lock = threading.Lock()
        
        # Load proxies from file if provided
        if proxy_file:
            self.load_proxies(proxy_file)
    
    def load_proxies(self, proxy_file: str):
        """Load proxies from file"""
        try:
            with open(proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(self.proxies)} proxies from {proxy_file}")
        except FileNotFoundError:
            print(f"Proxy file {proxy_file} not found")
        except Exception as e:
            print(f"Error loading proxies: {e}")
    

    
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        with self.proxy_lock:
            proxy = self.proxies[self.current_proxy_index]
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
            return proxy
    
    def create_channel(self) -> grpc.Channel:
        """Create gRPC channel with SSL and proxy support"""
        options = [
            ('grpc.keepalive_time_ms', 30000),
            ('grpc.keepalive_timeout_ms', 10000),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.http2.min_time_between_pings_ms', 10000),
            ('grpc.http2.min_ping_interval_without_data_ms', 300000),
            ('grpc.max_receive_message_length', -1),
            ('grpc.max_send_message_length', -1),
            ('grpc.primary_user_agent', 'grpc-python/1.71.2'),
        ]
        
        # Get proxy if available
        proxy = self.get_next_proxy()
        if proxy:
            return self.create_channel_with_proxy(proxy, options)
        else:
            # No proxy - direct connection
            if self.insecure:
                return grpc.insecure_channel(self.target, options=options)
            else:
                credentials = ssl_channel_credentials()
                return grpc.secure_channel(self.target, credentials, options=options)
    
    def create_channel_with_proxy(self, proxy: str, options: List[tuple]) -> grpc.Channel:
        if not proxy.startswith('http://') and not proxy.startswith('https://'):
            proxy = f'http://{proxy}'
        
        old_http_proxy = os.environ.get('HTTP_PROXY')
        old_https_proxy = os.environ.get('HTTPS_PROXY')
        
        try:
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
            
            if self.insecure:
                channel = grpc.insecure_channel(self.target, options=options)
            else:
                credentials = ssl_channel_credentials()
                channel = grpc.secure_channel(self.target, credentials, options=options)
            
            return channel
            
        except Exception:
            if old_http_proxy:
                os.environ['HTTP_PROXY'] = old_http_proxy
            else:
                os.environ.pop('HTTP_PROXY', None)
            
            if old_https_proxy:
                os.environ['HTTPS_PROXY'] = old_https_proxy
            else:
                os.environ.pop('HTTPS_PROXY', None)
            
            if self.insecure:
                return grpc.insecure_channel(self.target, options=options)
            else:
                credentials = ssl_channel_credentials()
                return grpc.secure_channel(self.target, credentials, options=options)
    
    def create_metadata(self, metadata_dict: Dict[str, str]) -> List[tuple]:
        """Convert metadata dictionary to gRPC metadata format"""
        metadata = [(key, value) for key, value in metadata_dict.items()]
        
        # Выбираем правильный content-type
        if self.grpc_web:
            content_type = 'application/grpc-web+proto'
        else:
            content_type = 'application/grpc+proto'
        
        # Добавляем стандартные gRPC заголовки
        metadata.extend([
            ('content-type', content_type),
            ('te', 'trailers'),
            ('grpc-accept-encoding', 'gzip')
        ])
        return metadata
    
    def single_request(self, data: Dict, metadata: Dict[str, str], timeout: float = 10.0) -> Dict:
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
                    timeout=timeout
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
    
    def worker_thread(self, data: Dict, metadata: Dict[str, str], request_count: int, timeout: float) -> List[Dict]:
        """Worker thread to perform multiple requests"""
        results = []
        for _ in range(request_count):
            result = self.single_request(data, metadata, timeout)
            results.append(result)
            
            with self.lock:
                self.results.append(result)
                
        return results
    
    def run_load_test(self, 
                     data: Dict, 
                     metadata: Dict[str, str], 
                     concurrency: int = 1, 
                     total_requests: int = 20, 
                     duration: Optional[float] = None,
                     timeout: float = 10.0) -> Dict:
        """Run load test with specified parameters"""
        
        print(f"Starting load test...")
        print(f"Target: {self.target}")
        print(f"Concurrency: {concurrency}")
        print(f"Total requests: {total_requests}")
        if duration:
            print(f"Duration: {duration}s")
        print(f"Timeout: {timeout}s")
        print("-" * 50)
        
        self.results = []
        start_time = time.time()
        
        if duration:
            # Duration-based test
            end_time = start_time + duration
            requests_per_thread = total_requests // concurrency
            
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = []
                for _ in range(concurrency):
                    future = executor.submit(
                        self.duration_worker, 
                        data, metadata, end_time, timeout
                    )
                    futures.append(future)
                
                # Wait for all threads to complete
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Worker thread error: {e}")
        else:
            # Request count-based test
            requests_per_thread = total_requests // concurrency
            remaining_requests = total_requests % concurrency
            
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = []
                for i in range(concurrency):
                    thread_requests = requests_per_thread + (1 if i < remaining_requests else 0)
                    future = executor.submit(
                        self.worker_thread, 
                        data, metadata, thread_requests, timeout
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
    
    def duration_worker(self, data: Dict, metadata: Dict[str, str], end_time: float, timeout: float):
        """Worker that runs for a specific duration"""
        while time.time() < end_time:
            result = self.single_request(data, metadata, timeout)
            with self.lock:
                self.results.append(result)
    
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
    
    def print_pretty_report(self, report: Dict):
        """Print report in pretty format"""
        print("\n" + "="*50)
        print("LOAD TEST RESULTS")
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
    parser = argparse.ArgumentParser()
    parser.add_argument('target', nargs='?', default='newibankdevcorp.kicb.net:443')
    parser.add_argument('--proto', default='protofile.proto')
    parser.add_argument('--call', default='dmz_api.WebAuthApi/authenticate')
    parser.add_argument('-d', '--data', default='{"username":"01229","password":"password1"}')
    parser.add_argument('-m', '--metadata', default='{"refid":"45f465bf-9729-40bc-b78e-78e678d6cc52","device-type":"ios","user-agent":"15_Iphone_16_pro"}')
    parser.add_argument('--concurrency', type=int, default=5)
    parser.add_argument('--total', type=int, default=100)
    parser.add_argument('--duration', type=float)
    parser.add_argument('--timeout', type=float, default=10.0)
    parser.add_argument('--format', default='pretty', choices=['pretty', 'json'])
    parser.add_argument('--insecure', action='store_true', default=False)
    parser.add_argument('--grpc-web', action='store_true', help='Use gRPC-Web content type')
    parser.add_argument('--proxy-file')
    
    args = parser.parse_args()
    
    # Parse data and metadata
    try:
        data = json.loads(args.data)
        metadata = json.loads(args.metadata)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return 1
    
    # Create tester
    tester = GrpcStressTester(args.target, args.proto, args.insecure, args.proxy_file, args.grpc_web)
    
    # Run test
    try:
        report = tester.run_load_test(
            data=data,
            metadata=metadata,
            concurrency=args.concurrency,
            total_requests=args.total,
            duration=args.duration,
            timeout=args.timeout
        )
        
        if args.format == 'pretty':
            tester.print_pretty_report(report)
        else:
            print(json.dumps(report, indent=2))
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"Error during test: {e}")
        return 1
    
    return 0


class LoadTestConfig:
    def __init__(self):
        self.target = "newibankdevcorp.kicb.net:443"
        self.proto_file = "protofile.proto"
        self.insecure = False
        
        self.data = {"username": "01229", "password": "password1"}
        self.metadata = {
            "refid": "45f465bf-9729-40bc-b78e-78e678d6cc52",
            "device-type": "ios",
            "user-agent": "15_Iphone_16_pro"
        }
        
        self.concurrency = 5
        self.total_requests = 100
        self.duration = None
        self.timeout = 10.0
        
        self.proxy_file = "working_proxies.txt"
        self.format = "pretty"
        self.verbose = True
        self.grpc_web = False
    
    def run_test(self):
        tester = GrpcStressTester(
            self.target, 
            self.proto_file, 
            self.insecure, 
            self.proxy_file,
            self.grpc_web
        )
        
        try:
            report = tester.run_load_test(
                data=self.data,
                metadata=self.metadata,
                concurrency=self.concurrency,
                total_requests=self.total_requests,
                duration=self.duration,
                timeout=self.timeout
            )
            
            if self.format == 'pretty':
                tester.print_pretty_report(report)
            else:
                print(json.dumps(report, indent=2))
                
        except KeyboardInterrupt:
            print("\nTest interrupted")
        except Exception as e:
            print(f"Error: {e}")


def run_custom_test():
    config = LoadTestConfig()
    
    config.concurrency = 5
    config.total_requests = 100
    config.duration = None
    config.timeout = 5
    
    config.data = {"username": "01229", "password": "password1"}
    config.proxy_file = "working_proxies.txt"
    
    config.run_test()





if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "custom":
        run_custom_test()
        sys.exit(0)
    
    sys.exit(main())
