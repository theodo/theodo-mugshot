# Automatic profile picture cropping and centering

Helping users crop and center their profile picture is certainly a nice-to-have feature you can find in every web project in which users have a profile.

I was faced with this problem again in a different context. The team page is the second most visited page on our website, certainly because we have put the pictures of everyone in the team, which is a great way for visitors to have a feel of who we are. But there are often faces missing on this page! With people arriving almost every week, it has become cumbersome to crop, center and upload the picture manually... I guess it is time to automate!

I wanted to try something more ambitious than just a cropping interface: I wanted to detect the face and the eyes automatically. It is a very challenging computer vision problem, but as usual there is a trivial solution in Python. First install the python-opencv package

```bash
# On Ubuntu
sudo apt-get install python-opencv
```

Then download the two "feature" files, trained on thousands of image to detect faces and eyes :

 - haarcascade_frontalface_default.xml
 - haarcascade_eye.xml

And then it is a matter of a few lines:

```python
import cv2

image = cv2.imread(filename)

haarFeatures = cv2.cv.Load('haarcascade_frontalface_default.xml')
faces = cv2.cv.HaarDetectObjects(cv2.cv.fromarray(image), haarFeatures, cv2.cv.CreateMemStorage())

haarFeatures = cv2.cv.Load('haarcascade_eye.xml')
eyes = cv2.cv.HaarDetectObjects(cv2.cv.fromarray(image), haarFeatures, cv2.cv.CreateMemStorage())
```

If `import cv2` triggers the following warning: `libdc1394 error: Failed to initialize libdc1394` just ignore it, it means the webcam was not detected.

This example is quite emblematic of the good and the bad in the Python world:
 - amazingly good: as often two lines are enough to use a really complex algorithm, based on recent academic results
 - sad: cv and cv2 coexist just like Python2 and Python3, which can be a little confusing. cv2 is more powerful because you can use images as numpy arrays, but many functions have not been ported to cv2 yet... The easy compromise for the moment: you can access the cv libray in cv2 with cv2.cv. And you can easily convert images from cv2 to cv with cv2.cv.fromarray(image)

If you try these few lines on this <a>picture of me</a>, here is what you get:

```python
>>> print faces
[((200, 282, 351, 351), 100)]
>>> print eyes
[((273, 382, 76, 76), 127), ((396, 388, 70, 70), 193), ((318, 603, 92, 92), 6)]
```

The result is the list of detected rectangles, for example (200, 282, 351, 351) for my face, with an additional value: the "number of neighbors", for example 100 for my face.

So we can see the algorithm did find my face, but he found three eyes instead of two... hmmh. That is when the "number of neighbors" comes in handy. It corresponds to the number of times something like a face or an eye was found in the same region. So actually the algorithm found 127+193+6=326 eyes in my picture! He then grouped them in three groups, among which on has clearly less "neighbors", it is the one we will discard:

```python
if len(eyes) > 1:
  eyes = sorted(eyes, key=lambda eye: eye[1], reverse=True)

eyes = eyes[:2]
```

Now that we have this information, to automatically crop and center we need to decide two things:
 - how relatively big we want the face to be on the picture?
 - where we want to center the face?

After some trials, I chose:
 - 0.61803397 as the ideal ratio for faceWidth/resultWidth. Why so much precision? Because it is the golden ratio-1 :-)
 - (0.5, 0.46) as the ideal coordinates for the eyes center

```python
# after some treatment we suppose we have
# face = (200, 282, 351, 351)
# eyesCenter = (371, 421)

idealFaceWidth = 0.61803397
idealEyesCenter = (0.5, 0.46)

resultWidth = int(face[3] / idealFaceWidth)
left = int(eyesCenter[0] - idealEyesCenter[0] * resultWidth)
top  = int(eyesCenter[1] - idealEyesCenter[1] * resultWidth)

resultImage = image[top:(top + resultWidth), left:(left + resultWidth)]

cv2.imwrite(outputFilename, resultImage)
```

And here is the result! On my face it works really well :-)



