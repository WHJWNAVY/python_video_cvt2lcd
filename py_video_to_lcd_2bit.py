import numpy as np
import cv2
import math
import datetime

def math_pow(x, n):
    sum = 1
    for i in range(n):
        sum = sum*x
    return sum

def lcdCvtGrayColor(colGray, colDepth):
    COL_DIV = 256 // colDepth

    for i in range(colDepth - 1, -1, -1):
        if colGray >= COL_DIV * i:
            return colDepth - 1 - i
    return colDepth - 1

LCD_WIDTH = 192
LCD_HEIGHT = 96

_DEFAULT_GAUSSIAN_BLUR_KERNEL = (5, 5)
_DEFAULT_THRESHOLD_TYPE = cv2.THRESH_BINARY + cv2.THRESH_OTSU  # cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU

VIDEO_NAME = input("Please Input Video Name With Full Path:")
# VIDEO_NAME = r"F:\RaspberryPi2\BadApple\VideoToLCD_Python\nokia_lumia_925.mp4"
# VIDEO_NAME = r"F:\RaspberryPi2\BadApple\VideoToLCD_Python\BadApple.mp4" # Time Consuming: 244 seconds
# VIDEO_NAME = VIDEO_NAME.replace("\\", "/")

print("Video Name:", VIDEO_NAME)

if VIDEO_NAME == None or len(VIDEO_NAME) == 0:
    print("Error Video Name!")
    exit()

# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(VIDEO_NAME)

if cap.isOpened() == False:
    print("Open Video File Faild!")
    exit()

# 获取视频帧率
VIDEO_FPS = cap.get(cv2.CAP_PROP_FPS)
VIDEO_FPS = int(round(VIDEO_FPS))  # 四舍五入
print("Video FPS:", VIDEO_FPS)

# 获取视频帧数
VIDEO_FFRAME = cap.get(cv2.CAP_PROP_FRAME_COUNT)
VIDEO_FFRAME = int(round(VIDEO_FFRAME))  # 四舍五入
print("Video Frame Count:", VIDEO_FFRAME)

# 获取视频帧大小
VIDEO_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
VIDEO_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
VIDEO_WIDTH = int(round(VIDEO_WIDTH))  # 四舍五入
VIDEO_HEIGHT = int(round(VIDEO_HEIGHT))  # 四舍五入
print("Video Size: (", VIDEO_WIDTH, VIDEO_HEIGHT, ")")

print("LCD Size: (", LCD_WIDTH, LCD_HEIGHT, ")")

# 计算图像缩放比例
VIDEO_WSCAL = LCD_WIDTH / VIDEO_WIDTH
VIDEO_HSCAL = LCD_HEIGHT / VIDEO_HEIGHT
VIDEO_SCAL = min(VIDEO_WSCAL, VIDEO_HSCAL) # 等比缩放
LCD_WIDTH = int(VIDEO_WIDTH * VIDEO_SCAL)
LCD_HEIGHT = int(VIDEO_HEIGHT * VIDEO_SCAL)
print("Video Scaling Ratio: (", VIDEO_WSCAL, VIDEO_HSCAL, ")")
print("Resize Video Size To: (", LCD_WIDTH, LCD_HEIGHT, ")")

LCD_IMAGE_PIXEL_BIT = 2
LCD_IMAGE_COLOUR_DEPTH = math_pow(2, LCD_IMAGE_PIXEL_BIT)

timenow = datetime.datetime.now()
timestr = timenow.strftime("%Y-%m-%d-%H-%M-%S")

LCD_IMAGE_FILE_NAME = "{0}_{1}x{2}_{3}fps_{4}frame_{5}bit_{6}.bin".format(VIDEO_NAME, LCD_WIDTH, LCD_HEIGHT, VIDEO_FPS, VIDEO_FFRAME, LCD_IMAGE_PIXEL_BIT, timestr)
# print("LCD Image File:", LCD_IMAGE_FILE_NAME)
LCD_IMAGE_FILE = open(LCD_IMAGE_FILE_NAME, "wb")

# 写入镜像文件头信息
'''
typedef struct lcd_video_img_hdr_s
{
    int32_t     flag;           //file flag, "LVIF"
    int32_t     video_width;    //video width, 1920
    int32_t     video_height;   //video height, 1080
    int32_t     lcd_width;      //lcd width, 128
    int32_t     lcd_height;     //lcd height, 64
    int32_t     video_fps;      //video fps, 25
    int32_t     video_frame;    //video frame count, 875
    int32_t     pixel_bit;      //每个像素点所占的bit
} lcd_video_img_hdr_t;
'''

LCD_IMAGE_HEADER = np.array([VIDEO_WIDTH, VIDEO_HEIGHT, LCD_WIDTH, LCD_HEIGHT, VIDEO_FPS, VIDEO_FFRAME, LCD_IMAGE_PIXEL_BIT], dtype=np.int32)
LCD_IMAGE_HEADER = bytearray(LCD_IMAGE_HEADER)
LCD_IMAGE_FILE.write(bytearray(b"LVIF"))
LCD_IMAGE_FILE.write(LCD_IMAGE_HEADER)

process_bar = 0
process_time0 = 0
process_time1 = 0
frmcnt = 0
print("Start Process!")
process_time0 = datetime.datetime.now()

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        # frame = cv2.flip(frame, 0) # 旋转

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 灰度化

        # frame = cv2.resize(frame, None, fx=VIDEO_SCAL, fy=VIDEO_SCAL, interpolation=cv2.INTER_CUBIC)  # 改变大小,等比缩放
        frame = cv2.resize(frame,  (LCD_WIDTH, LCD_HEIGHT), interpolation=cv2.INTER_CUBIC)  # 改变大小，按尺寸缩放

        # print("Img Size: ", frame.shape)

        # print(frame.dtype)
        # print(frame.shape[0], frame.shape[1])

        # 显示视频帧
        cv2.imshow(VIDEO_NAME, frame)

        # 写入镜像文件
        if LCD_IMAGE_PIXEL_BIT == 8:
            LCD_IMAGE_FILE.write(bytearray(frame))
        elif LCD_IMAGE_PIXEL_BIT == 1:
            frame = cv2.GaussianBlur(frame, ksize=_DEFAULT_GAUSSIAN_BLUR_KERNEL, sigmaX=0)  # 高斯模糊
            _, frame = cv2.threshold(frame, 0, 255, _DEFAULT_THRESHOLD_TYPE)  # 二值化

            # Time Consuming: 57 seconds

            byten = 0
            bytei = 0
            frame.dtype = np.bool
            arrya_x = math.ceil(LCD_WIDTH / 8)
            array_y = LCD_HEIGHT  # array_y = math.ceil(LCD_HEIGHT / 8)
            byte_arry = np.zeros((arrya_x*array_y), dtype=np.uint8)

            for y in range(LCD_HEIGHT):  # range(frame.shape[0]):
                for x in range(LCD_WIDTH):  # range(frame.shape[1]):
                    # print(byte_arry[byten])
                    if ((x % 8) == 0) and (x != 0):
                        byte_arry[bytei] = byten
                        bytei += 1
                        byten = 0

                    byten = byten << 1
                    if frame[y][x] != False:
                        byten = byten | 1
                    else:
                        pass
                    # print(bytei, byten)
                byte_arry[bytei] = byten
                bytei += 1
                byten = 0

            # print(byte_arry.size, byten)
            LCD_IMAGE_FILE.write(bytearray(byte_arry))
        elif LCD_IMAGE_PIXEL_BIT == 2:
            # Time Consuming: 57 seconds

            byten = 0
            bytei = 0
            frame.dtype = np.uint8

            array_page = math.ceil(LCD_HEIGHT / LCD_IMAGE_COLOUR_DEPTH)
            array_x = LCD_WIDTH
            array_y = array_page
            byte_arry = np.zeros((array_x*array_y), dtype=np.uint8)

            for page in range(array_page):
                for x in range(LCD_WIDTH):
                    byten = 0
                    for i in range(LCD_IMAGE_COLOUR_DEPTH):
                        y = (page * LCD_IMAGE_COLOUR_DEPTH) + i
                        if y >= LCD_HEIGHT:
                            col = 0
                        else:
                            col = lcdCvtGrayColor(frame[y][x], LCD_IMAGE_COLOUR_DEPTH)
                        # print("x, y, page, col0 = ", x, y, page, col)
                        '''
                        BIT_MAP: | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
                        Y_DOT  : |   0   |   1   |   2   |   3   |
                        '''
                        bitmv = LCD_IMAGE_COLOUR_DEPTH - i - 1
                        col = col * math_pow(2, bitmv * 2) # col = (col << (2 * bitmv))
                        # print("x, y, page, col1 = ", x, y, page, col)
                        byten = (byten + col)
                    byte_arry[bytei] = byten
                    # print("byte_arry.size, bytei, byten = ", byte_arry.size, bytei, byten)
                    bytei += 1
                    byten = 0
                LCD_IMAGE_FILE.write(bytearray(byte_arry))
        else:
            pass
        frmcnt += 1
        print("Frame Count:", frmcnt)
        # 显示进度
        print("#", end="", flush=True)
        process_bar += 1
        if process_bar >= 60:  # 大于60换行
            process_bar = 0
            print("")
    else:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # cv2.waitKey(1)
print("\nAll Frame Count:", frmcnt)
print("Process Done!")
LCD_IMAGE_FILE.close()
print("Save LCD Image File to:", LCD_IMAGE_FILE_NAME)

process_time1 = datetime.datetime.now()
process_time1 = process_time1 - process_time0

print("Time Consuming:", process_time1.seconds, "seconds")

cap.release()
cv2.destroyAllWindows()
