# Student Management System — Android APK project

This is an Android-compatible rewrite of the Tkinter student manager using Kivy.
It includes admin login, home screen, student CRUD, search, and a local SQLite database.

## Demo login
- Username: `admin`
- Password: `admin123`

## Build an APK using GitHub Actions (recommended)
1. Create a GitHub account if you do not have one.
2. Create a new repository and upload all files in this ZIP.
3. Open the repository's **Actions** tab.
4. Select **Build Android APK** and press **Run workflow** (or push a commit).
5. Wait for the workflow to finish.
6. Open the completed workflow run and download the `student-management-apk` artifact.
7. Extract the artifact and install the APK on your Android phone. Android may ask you to allow installation from that source.

## Build locally
On Ubuntu/Linux with Java, Android SDK/NDK prerequisites installed:
```bash
python -m pip install --upgrade pip
pip install buildozer cython
buildozer android debug
```
The APK will be created in the `bin/` folder.

## Important
- The SQLite database is stored in the app's private Android data directory.
- The demo login is hardcoded and is not suitable for production use. Change it before real deployment.
- This ZIP contains the complete app source and automated APK build workflow, not a precompiled APK.
