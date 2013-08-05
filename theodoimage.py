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

def detectEyes(imcolor):
    """
    Returns the rectangles around the two most visible eyes in the image
    """

    eyeRectangles = detectRectangles(imcolor, 'haarcascade_eye.xml')

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

    return eyescenter

def cropAroundFaceAndEyes(image, face, eyes, idealfacewidth, idealeyecenter):
    """
    Crops an image using ideal face width and ideal eyes position
    """

    center = geteyescenter(eyes)

    size = int(face[3] / idealfacewidth)
    left = int(center[0] - idealeyecenter[0] * size)
    top  = int(center[1] - idealeyecenter[1] * size)

    if left < 0 or top < 0:
        minleft = idealeyecenter[0] * face[3] / center[0]
        mintop  = idealeyecenter[1] * face[3] / center[1]
        raise Exception('Face on original picture is too big for this ideal face width ratio. Minimum: ' + str(max(minleft, mintop)))

    return image[top:(top + size), left:(left + size)]
