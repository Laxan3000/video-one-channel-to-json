#!/usr/bin/python
from typing import Generator, Callable
import cv2 as cv

VIDEO_INPUT_NAME = "input.mp4"
JSON_OUTPUT_NAME = 'result.json'
RESIZE_INTER = cv.INTER_AREA
CHANNEL = 0

#* Must be multiples of the video's aspect ratio
JSON_WIDTH = 8
JSON_HEIGHT = 6

#* Skip SKIP_AMOUNT frames after FRAME_SKIP. Set to -1 to disable
FRAME_SKIP = -1
SKIP_AMOUNT = 1

#* The number outputted to the JSON for each pixel inside the channel. v stand for value
FORMULA: Callable[[int], int] = lambda v: v


def rescale_frame(frame: cv.typing.MatLike) -> cv.typing.MatLike:
    return cv.resize(
        src=frame,
        dsize=(JSON_WIDTH, JSON_HEIGHT),
        interpolation=RESIZE_INTER
    )


def read_frames(cap: cv.VideoCapture) -> Generator[cv.typing.MatLike, None]:
    while cap.isOpened():
        current_frame = cap.get(cv.CAP_PROP_POS_FRAMES)
        if FRAME_SKIP and current_frame % FRAME_SKIP == FRAME_SKIP - 1:
            cap.set(cv.CAP_PROP_POS_FRAMES, current_frame + SKIP_AMOUNT)
        
        ret, frame = cap.read()
        
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        #* Not needed since only a channel is used anyway
        # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        
        yield rescale_frame(frame)


def generate_json(generator: Generator[cv.typing.MatLike, None]) -> None:
    json = "[\n\t"
    for frame in generator:
        #* Uncomment to see generation process
        # cv.imshow("Output", frame)
        # if (cv.waitKey(1) & 0xFF) == ord('q'):
        #     cv.destroyWindow("Output")

        json += "[\n\t\t"
        for x in range(0, JSON_HEIGHT):
            json += f"[{','.join([str(FORMULA(int(frame[x,y,CHANNEL]))) for y in range(0, JSON_WIDTH)])}]"
            json += ",\n\t\t" if x < JSON_HEIGHT - 1 else "\n\t],\n\t"
    else:
        json = json[:-3]
    if json: json += "\n]"
    
    with open(JSON_OUTPUT_NAME, "w") as f:
        f.write(json)
    

if __name__ == '__main__':
    cap = cv.VideoCapture(VIDEO_INPUT_NAME)
    
    assert cap.get(cv.CAP_PROP_FRAME_WIDTH)/cap.get(cv.CAP_PROP_FRAME_HEIGHT) == JSON_WIDTH/JSON_HEIGHT, \
    f"JSON_WIDTH/JSON_HEIGHT ({JSON_WIDTH}/{JSON_HEIGHT}) is not the same aspect ratio from source!"
    
    generate_json(read_frames(cap))
    
    cap.release()
    
    print("Should be all done!")