@echo off
echo Creating requirements.txt file...

rem Create a requirements.txt file with the package names (without versions)
(
echo asgiref
echo certifi
echo cffi
echo charset-normalizer
echo cloudinary
echo Django
echo django-cors-headers
echo djangorestframework
echo django-cleanup
echo idna
echo milksnake
echo mysqlclient
echo pillow
echo python-dotenv
echo pycparser
echo pytz
echo requests
echo six
echo sqlparse
echo tzdata
echo urllib3
echo urlquote
echo whitenoise
echo opencv-python
) > requirements.txt

echo Installing packages...

rem Install the packages from the requirements.txt file
pip install -r requirements.txt --upgrade

echo Installation complete!
pause