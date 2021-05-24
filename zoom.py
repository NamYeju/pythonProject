import cv2
import datetime

global scale
global scale2
global center_x, center_y
click = False
s = False
scale2 = 0.9
x = 0  # 움직임 x 좌표변수
y = 0  # 움직임 y 좌표변수
record = False

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


def nothing():  # 트랙바 함수
    pass


def get_scale():
    global scale
    scale = 1 - (cv2.getTrackbarPos('zoom', 'Camera') / 10)
    #print(scale)

    return scale


def onMouse(event, x, y, flags, param):     # 마우스이벤트함수
    global center_x, center_y, scale2, click, s
    s = False
    if event == cv2.EVENT_LBUTTONDOWN:
        click = True
        center_x, center_y = x, y
        if s is False:
            scale2 = scale2 - 0.1
            s = True

    if event == cv2.EVENT_RBUTTONDOWN:
        click = True
        center_x, center_y = x, y
        if s is False:
            scale2 = scale2 + 0.1
            s = True


cv2.namedWindow('Camera')
cv2.createTrackbar('zoom', 'Camera', 1, 10, nothing)
cv2.setMouseCallback('Camera', onMouse)

while cap.isOpened():
    # 카메라 프레임 읽기
    success, frame = cap.read()

    if success:

        # 좌우반전하여 프레임 출력
        ret, np_image = cap.read()
        np_image = cv2.flip(np_image, 1)
        frame = np_image
        cv2.imshow('Camera', frame)

        height, width = np_image.shape[:2]

        # 캠 가운데 중심으로 확대축소
        if click is False:
            scale = get_scale()

            center_x = int(width/2)
            center_y = int(height/2)

            radius_x, radius_y = int(width / 2), int(height / 2)
            radius_x, radius_y = int(scale * radius_x), int(scale * radius_y)

        # 특정 위치 확대 축소
        if click is True:

            #print(scale2)

            #   비율 범위에 맞게 중심값 계산
            rate = height / width

            if center_x < width * (1-rate):
                center_x = width * (1-rate)
            elif center_x > width * rate:
                center_x = width * rate
            if center_y < height * (1-rate):
                center_y = height * (1-rate)
            elif center_y > height * rate:
                center_y = height * rate

            center_x, center_y = int(center_x), int(center_y)   # float를 int형으로 변환
            left_x, right_x = center_x, int(width-center_x)
            up_y, down_y = int(height-center_y), center_y
            radius_x = min(left_x, right_x)
            radius_y = min(up_y, down_y)
            radius_x, radius_y = int(scale2 * radius_x), int(scale2 * radius_y)

        # size 계산
        min_x, max_x = center_x-radius_x, center_x+radius_x
        min_y, max_y = center_y-radius_y, center_y+radius_y

        # size에 맞춰 이미지를 자른다
        cropped = np_image[min_y:max_y, min_x:max_x]
        # 원래 사이즈로 늘리기
        new_cropped = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_CUBIC)

        # 움직임이벤트
        key = cv2.waitKeyEx(1)
        if (scale != 1) and (key == 0x270000):   # right
            x += 10
            #ret, scale

        elif (scale != 1) and (key == 0x250000):   # left
            x -= 10
            #ret, scale

        elif (scale != 1) and (key == 0x280000):   # down
            y += 10
            #ret, scale

        elif (scale != 1) and (key == 0x260000):   # up
            y -= 10
            #ret, scale

        if key == 27:
            break

        cropped = np_image[min_y+y:max_y+y, min_x + x:max_x + x]  # x,y좌표 만큼 화면 이동
        new_cropped = cv2.resize(cropped, (width, height))  # 원래 사이즈로 맞추기

        cv2.imshow('Camera', new_cropped)

        # 카메라 찍기
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d')
        hour = now.strftime('%H%M%S')
        filename = 'img/{}_{}.png'.format(date, hour)

        # 비디오 녹화
        fps = 25.40
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_filename = 'img/{}_{}.avi'.format(date, hour)

        if record is True:
            print("녹화중")
            out.write(new_cropped)

        # 종료
        key = cv2.waitKey(33) & 0xFF
        if key == 27:  # esc -> 프로그램 종료
            break
        elif key == 26:   # 이미지 찍기 ctrl+z
            print("camera img start")
            cv2.imwrite(filename, new_cropped)
        elif key == ord('w'):  # 동영상 녹화 시작
            print("녹화시작")
            record = True
            out = cv2.VideoWriter(video_filename, fourcc, fps, (new_cropped.shape[1], new_cropped.shape[0]))
        elif key == ord('e'):   # 동영상 녹화 중지
            print("녹화중지")
            record = False

cap.release()
cv2.destroyAllWindows()