$ErrorActionPreference = 'Continue'
python --version
python -m pip --version
node --version
npm.cmd --version
git --version
docker --version
docker compose version
$projectRoot = Split-Path -Parent $PSScriptRoot
if (Test-Path (Join-Path $projectRoot '.venv/Scripts/python.exe')) {
    & (Join-Path $projectRoot '.venv/Scripts/python.exe') -c "import torch,imageio_ffmpeg; print('PyTorch:',torch.__version__,'CUDA:',torch.cuda.is_available()); print('FFmpeg:',imageio_ffmpeg.get_ffmpeg_exe())"
}
Get-PSDrive -Name C | Select-Object Used,Free
