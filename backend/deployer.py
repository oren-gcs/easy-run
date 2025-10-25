import os, subprocess, re, shutil, select
def stream_command(command, log_file, status_file, work_dir=None, env=None):
    try:
        process = subprocess.Popen(command, cwd=work_dir, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        with open(log_file, 'a') as f:
            for line in process.stdout:
                f.write(line)
                print(line, end='')
        process.wait()
        if process.returncode != 0:
            with open(status_file, 'w') as f: f.write("failed")
            return False
        return True
    except Exception as e:
        with open(log_file, 'a') as f: f.write(f"\nCOMMAND FAILED: {e}\n")
        with open(status_file, 'w') as f: f.write("failed")
        return False
def find_terraform_directory(base_path, log_file):
    for root, _, files in os.walk(base_path):
        if any(f.endswith('.tf') for f in files): return root
    return None
def run_deployment_thread(config, log_file, status_file):
    with open(log_file, 'a') as f: f.write("Starting deployment...\n")
    git_url = config.get('gitUrl')
    source_dir = "/workspace/source"
    if os.path.exists(source_dir): shutil.rmtree(source_dir)
    os.makedirs(source_dir)
    if not stream_command(['git', 'clone', git_url, source_dir], log_file, status_file): return
    tf_dir = find_terraform_directory(source_dir, log_file)
    if not tf_dir: 
        with open(log_file, 'a') as f: f.write("Terraform files not found!\n")
        return
    with open(status_file, 'w') as f: f.write("success")