import subprocess

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

# Example
for path in execute(['xterm','-T', 'YoloV4', '-e', '/usr/bin/cb_console_runner', 'LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.:/usr/local/lib', '/home/pi/Documents/YoloDetect/bin/Release/YoloV4', 'parking.jpg']):
    print(path, end="")