# Copy New Files

Watches a directory for new files. New files get copied to a target directory once they stopped changing. Will try to wait for files to have finished changing (i.e. downloads) and try to retain the order in which the new files were created. The intended purpose was grabbing images from Firefox' cache to then process them elsewhere without the need for manual intervention during web surfing.

## Usage

Install dependencies. Change the directories the script should point to in main. Adjust desired file types and minimum image size if necessary.

## Issues

Will only check the oldest new file if it finished changing, so it will get stuck on a constantly changing file. This is no problem for me so I left it like that.