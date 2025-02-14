import tools.LCD_1in44 as screen
import RPi.GPIO as GPIO
import time
from PIL import Image,ImageDraw,ImageFont,ImageColor

KEY_U   = 6 
KEY_D   = 19
KEY_L   = 5
KEY_R   = 26
KEY_S   = 13
KEY_1   = 21
KEY_2   = 20
KEY_3   = 16

#init GPIO
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
GPIO.setup(KEY_U, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_D, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_L, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_R, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_S, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# 240x240 display with hardware SPI:
disp = screen.LCD()
Lcd_ScanDir = screen.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = 128
height = 128
image = Image.new('RGB', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)
disp.LCD_ShowImage(image,0,0)

# try:
while 1:
    # with canvas(device) as draw:
    if GPIO.input(KEY_U) == 0: # button is released       
        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0xff00)  #Up        
        print("Up")    
    else: # button is pressed:
        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up filled
        
    if GPIO.input(KEY_D) == 0: # button is released
        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0xff00) #down
        print("down")
    else: # button is pressed:
        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down filled

    if GPIO.input(KEY_L) == 0: # button is released
        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0xff00)  #left
        print("left")    
    else: # button is pressed:       
        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  #left filled
        
    if GPIO.input(KEY_R) == 0: # button is released
        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0xff00) #right
        print("right")
    else: # button is pressed:
        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0) #right filled       
        
    if GPIO.input(KEY_S) == 0: # button is released
        draw.rectangle((20, 22,40,40), outline=255, fill=0xff00) #center 
        print("center")
    else: # button is pressed:
        draw.rectangle((20, 22,40,40), outline=255, fill=0) #center filled
        
    if GPIO.input(KEY_1) == 0: # button is released
        draw.ellipse((70,0,90,20), outline=255, fill=0xff00) #A button
        print("KEY1")
    else: # button is pressed:
        draw.ellipse((70,0,90,20), outline=255, fill=0) #A button filled
        
    if GPIO.input(KEY_2) == 0: # button is released
        draw.ellipse((100,20,120,40), outline=255, fill=0xff00) #B button]
        print("KEY2")
    else: # button is pressed:
        draw.ellipse((100,20,120,40), outline=255, fill=0) #B button filled
        
    if GPIO.input(KEY_3) == 0: # button is released
        draw.ellipse((70,40,90,60), outline=255, fill=0xff00) #A button
        print("KEY3")
    else: # button is pressed:
        draw.ellipse((70,40,90,60), outline=255, fill=0) #A button filled
    disp.LCD_ShowImage(image,0,0)
# except:
	# print("except")
    # GPIO.cleanup()