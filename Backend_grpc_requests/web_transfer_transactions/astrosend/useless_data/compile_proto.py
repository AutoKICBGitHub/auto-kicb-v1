import os
import subprocess

def compile_proto():
    """Компилирует proto-файл в Python код."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    proto_file = os.path.join(current_dir, 'astrasend-internal-api.proto')
    
    # Создаем Python файлы из proto-файла
    subprocess.check_call([
        'python', '-m', 'grpc_tools.protoc',
        f'--proto_path={current_dir}',
        f'--python_out={current_dir}',
        f'--grpc_python_out={current_dir}',
        proto_file
    ])
    
    print(f"Proto-файл успешно скомпилирован: {proto_file}")

if __name__ == "__main__":
    compile_proto() 