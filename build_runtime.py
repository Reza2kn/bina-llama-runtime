import os, pathlib, shutil, subprocess, urllib.request

def run(*args): subprocess.run(args, check=True)
root=pathlib.Path.cwd()
if os.name=='nt':
    version='1.4.357.0'
    installer=root/'vulkan.exe'
    urllib.request.urlretrieve(f'https://sdk.lunarg.com/sdk/download/{version}/windows/vulkansdk-windows-X64-{version}.exe',installer)
    run(str(installer),'--accept-licenses','--default-answer','--confirm-command','install')
    sdk=pathlib.Path('C:/VulkanSDK')/version
    os.environ['VULKAN_SDK']=str(sdk)
    os.environ['PATH']=str(sdk/'Bin')+os.pathsep+os.environ['PATH']
else:
    run('sudo','apt-get','update')
    run('sudo','apt-get','install','-y','libvulkan-dev','glslc','ninja-build','spirv-headers')
run('git','clone','--depth','1','https://github.com/ggml-org/llama.cpp.git','upstream')
os.chdir('upstream')
run('git','fetch','--depth','1','origin','3057bb66c86c46d5781e50e85462a760ba7d1feb')
run('git','checkout','3057bb66c86c46d5781e50e85462a760ba7d1feb')
run('git','apply','../surya-wordlevel.patch')
os.chdir(root)
run('cmake','-S','upstream','-B','build','-DCMAKE_BUILD_TYPE=Release','-DGGML_NATIVE=OFF','-DGGML_VULKAN=ON','-DGGML_CUDA=OFF','-DLLAMA_CURL=OFF','-DLLAMA_BUILD_TESTS=OFF','-DLLAMA_BUILD_BORINGSSL=OFF')
run('cmake','--build','build','--config','Release','-j','4','--target','llama-mtmd-cli','llama-server')
package=root/'package'; package.mkdir(exist_ok=True)
binpath=root/'build/bin'
if (binpath/'Release').exists(): binpath=binpath/'Release'
for f in binpath.iterdir():
    if f.is_file(): shutil.copy2(f,package/f.name)
shutil.copy2('upstream/LICENSE',package/'LLAMA-LICENSE')
shutil.copy2('surya-wordlevel.patch',package)
for exe in ['llama-mtmd-cli','llama-server']:
    run(str(package/(exe+('.exe' if os.name=='nt' else ''))),'--version')
