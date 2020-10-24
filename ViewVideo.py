import cv2

if __name__ == '__main__':
    cap = cv2.VideoCapture("G:\\database\\trains\\trains_dataset\\archive_604799324.avi")
    while cap.isOpened():
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        height, width = frame.shape[:2]
        res = cv2.resize(frame, (int(width/2), int(height/2)), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('frame', res)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()