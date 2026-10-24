import {Config} from '@remotion/cli/config';

// Remotion kendi Chrome'unu indirmesin: önceden kurulu headless shell kullanılır.
Config.setBrowserExecutable(
  '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell',
);
Config.setVideoImageFormat('png');
Config.setCodec('h264');
Config.setCrf(22);
Config.setPixelFormat('yuv420p');
Config.setConcurrency(4);
Config.setOverwriteOutput(true);
