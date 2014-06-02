#!/usr/bin/env python
import sys
import cv2
import numpy


def appendGreyAndColorVersions(image):
    """
    image(w, h) -> image(w, 2*h)

    Creates a sprite out of an image with the greycolor version appended above the colour version
    """

    merged = numpy.zeros((2*image.shape[0], image.shape[1], 3))

    grey = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    for channel in range(3):
        merged[0:image.shape[0], 0:image.shape[1], channel] = grey

    merged[image.shape[0]:(2*image.shape[0]), 0:image.shape[1]] = image

    return merged

def detectRectangles(imcolor, feature_file):
    haarFeatures = cv2.cv.Load(feature_file)

    storage = cv2.cv.CreateMemStorage()

    rectangles = cv2.cv.HaarDetectObjects(cv2.cv.fromarray(imcolor), haarFeatures, storage)
    if len(rectangles) > 1:
        rectangles = sorted(rectangles, key=lambda detectedRectangle: detectedRectangle[1], reverse=True)

    return rectangles

def detectFace(imcolor):
    """
    Returns the rectangle around the most visible face in the image
    """

    faceRectangles = detectRectangles(imcolor, 'haarcascade_frontalface_default.xml')

    if len(faceRectangles) < 1:
        return None

    return faceRectangles[0][0]

def detectEyes(imcolor, face=None):
    """
    Returns the rectangles around the two most visible eyes in the image
    """

    eyeRectangles0 = detectRectangles(imcolor, 'haarcascade_eye.xml')
    if face:
        eyeRectangles = []
        for eyeRectangle in eyeRectangles0:
            if eyeRectangle[0][0] > face[0] and \
               eyeRectangle[0][1] > face[1] and \
               eyeRectangle[0][0] + eyeRectangle[0][2] < face[0] + face[2] and \
               eyeRectangle[0][1] + eyeRectangle[0][3] < face[1] + face[3] and \
               (len(eyeRectangles) < 1 or min(abs(eyeRectangle[0][0] - teyeRectangle[0][0]) for teyeRectangle in eyeRectangles) > 10):
                eyeRectangles.append(eyeRectangle)
    else:
        eyeRectangles = eyeRectangles0


    if len(eyeRectangles) < 2:
        return None

    return [eyeRectangle[0] for eyeRectangle in eyeRectangles[:2]]

def geteyescenter(eyes):
    """
    Returns the middle point between two eyes
    """

    eyescenter = (
        (eyes[0][0] + eyes[0][2]/2 + eyes[1][0] + eyes[1][2]/2) / 2,
        (eyes[0][1] + eyes[0][3]/2 + eyes[1][1] + eyes[1][3]/2) / 2
        )

    return eyescenter # Kenny:(700, 820)

def cropAroundFaceAndEyes(image, face, eyes, idealFaceWidth, idealEyesCenter, enlargeFace=True):
    """
    Crops an image using ideal face width and ideal eyes position
    """

    eyesCenter = geteyescenter(eyes)

    minleft = idealEyesCenter[0] * face[3] / eyesCenter[0]
    mintop  = idealEyesCenter[1] * face[3] / eyesCenter[1]
    if max(minleft, mintop) > idealFaceWidth and enlargeFace:
        print 'idealFaceWidth too small: ', idealFaceWidth
        idealFaceWidth = max(minleft, mintop) + 0.01
        print 'applying instead: ', idealFaceWidth

    resultWidth = int(face[3] / idealFaceWidth)
    left = int(eyesCenter[0] - idealEyesCenter[0] * resultWidth)
    top  = int(eyesCenter[1] - idealEyesCenter[1] * resultWidth)

    if left < 0 or top < 0:
        minleft = idealEyesCenter[0] * face[3] / eyesCenter[0]
        mintop  = idealEyesCenter[1] * face[3] / eyesCenter[1]
        raise Exception('Face on original picture is too big for this ideal face width ratio. Minimum: ' + str(max(minleft, mintop)))

    return image[top:(top + resultWidth), left:(left + resultWidth)]


def mugshotify(input_filename, output_filename, imagesize, idealFaceWidth, idealEyesCenter):
    source = cv2.imread(input_filename)

    face = detectFace(source)
    eyes = detectEyes(source, face)

    cropped = cropAroundFaceAndEyes(source, face, eyes, idealFaceWidth, idealEyesCenter)
    resized = cv2.resize(cropped, (imagesize, imagesize), interpolation=cv2.INTER_AREA)
    merged  = appendGreyAndColorVersions(resized)

    cv2.imwrite(output_filename, merged)
