from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework import status
import os
import subprocess
import tempfile
import logging
import requests
import base64

# Create your views here.
@api_view(['POST'])
@csrf_exempt
def print_photo(request):
    if request.method == 'POST':
        try:
            print("print_photo")
            folder_path = f"{os.getcwd()}\\print_files"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            image_file = request.data.get('photo')
            frame = request.data.get('frame')
            
            if not image_file or not frame:
                return JsonResponse({'error': 'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)
            
            print_url = settings.API_PRINTER_2
            print_file_name = ''
            if frame == 'Stripx2':
                print_file_name = 'stripx2.png'
                print_url = settings.API_PRINTER_CUT
            elif frame == '2cut-x2':
                print_file_name = 'cutx2.png'
                print_url = settings.API_PRINTER_2
            elif frame == '3-cutx2':
                print_file_name = 'cutx3.png'
                print_url = settings.API_PRINTER_3
            elif frame == '4-cutx2':
                print_file_name = 'cutx4.png'
                print_url = settings.API_PRINTER_4
            elif frame == '5-cutx2':
                print_file_name = 'cutx5.png'
                print_url = settings.API_PRINTER_5
            elif frame == '6-cutx2':
                print_file_name = 'cutx6.png'
                print_url = settings.API_PRINTER_6
            
            file_path = os.path.join(folder_path, print_file_name)

            print(111)
            print("file_path")
            print(file_path)
            print(111)

            print(f"Type of image_file: {type(image_file)}")
            print(f"Content of image_file: {image_file[:100] if isinstance(image_file, str) else 'Not a string'}")

            if isinstance(image_file, TemporaryUploadedFile):
                image_content = image_file.read()
            else:
                image_content = base64.b64decode(image_file)

            with open(file_path, 'wb') as destination:
                destination.write(image_content)

            if not os.path.exists(file_path):
                return JsonResponse({'error': 'Failed to save the file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return JsonResponse({'error': 'Saved file is empty'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Call POST method to printer                
            with open(file_path, 'rb') as f:
                for chunk in f.chunks():
                    f.write(chunk)

            try:
                print_image_with_rundll32(file_path, frame)
            except Exception as e:
                logging.error(f"Error processing print job: {e}")
                return JsonResponse({'error': str(e)}, status=500)
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"Error in print_photo: {str(e)}")
            print(f"Error type: {type(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)


# Print image using rundll32
def print_image_with_rundll32(image_path, frame_type):
    try:
        printer_name = 'DS-RX1 (Photostrips)' if frame_type == 'stripx2' else 'DS-RX1'
        logging.info(f"Printing to {printer_name}")

        print_command = f'rundll32.exe C:\\Windows\\System32\\shimgvw.dll,ImageView_PrintTo /pt "{image_path}" "{printer_name}"'
        logging.debug(f"Executing print command: {print_command}")

        subprocess.run(print_command, check=True, shell=True)
        logging.info(f"Print command sent for file: {image_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error printing file: {e}")
        raise