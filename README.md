# FolderScanner
### Folder scanner is an application that scans selected folder looking for sizes of the subdirectories and the main folder.

To run it on your machine make sure you're using python 3.10 **(no certainty that it will work on higher or lower versions)**
Install PyQt6 libraries on your virtual environment:
```
pip install -r requirements.txt
```

And run the program:
```
python main.py
```

You'll be greeted with a window where you can:
* Choose a directory.
* Scan the chosen directory.
* Cancel the scan and show scanned data to that point.

![image](https://github.com/user-attachments/assets/d2baece8-b4e1-42dc-9fc2-0b6d6ade3fd0)

At the bottom all the statistics will be shown of the current scan.

You can save the displayed data to a file in left right corner as a json file or load one.

When scanned data is displayed you can right click on a subdirectory to copy full path for your needs.

![image](https://github.com/user-attachments/assets/d6582d6f-f044-42de-aac5-ef838b127a3b)
