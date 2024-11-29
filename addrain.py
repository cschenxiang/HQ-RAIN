import cv2
import numpy as np
import glob
import os
import argparse
import random

def get_noise(img, value=10):

    noise = np.random.uniform(0, 256, img.shape[0:2])
    v = value * 0.01
    noise[np.where(noise < (256 - v))] = 0

    k = np.array([[0, 0.1, 0],
                  [0.1, 8, 0.1],
                  [0, 0.1, 0]])

    noise = cv2.filter2D(noise, -1, k)

    return noise


def rain_blur(noise, length=10, angle=0, w=1):

    trans = cv2.getRotationMatrix2D((length / 2, length / 2), angle - 45, 1 - length / 100.0)
    dig = np.diag(np.ones(length))  
    k = cv2.warpAffine(dig, trans, (length, length))  
    k = cv2.GaussianBlur(k, (w, w), 0) 

    # k = k / length                        

    blurred = cv2.filter2D(noise, -1, k) 

    cv2.normalize(blurred, blurred, 0, 255, cv2.NORM_MINMAX)
    blurred = np.array(blurred, dtype=np.uint8)

    return blurred


def alpha_rain(rain, img, img_name, out_dir, beta=0.8):

    rain = np.expand_dims(rain, 2)
    rain_effect = np.concatenate((img, rain), axis=2)  # add alpha channel

    rain_result = img.copy()  
    rain = np.array(rain, dtype=np.float32)  
    rain_result[:, :, 0] = rain_result[:, :, 0] * (255 - rain[:, :, 0]) / 255.0 + beta * rain[:, :, 0]
    rain_result[:, :, 1] = rain_result[:, :, 1] * (255 - rain[:, :, 0]) / 255 + beta * rain[:, :, 0]
    rain_result[:, :, 2] = rain_result[:, :, 2] * (255 - rain[:, :, 0]) / 255 + beta * rain[:, :, 0]

    cv2.imwrite(os.path.join(out_dir, os.path.basename(img_name)), rain_result)


def add_rain(rain, img, img_name, out_dir, alpha=0.9):

    rain = np.expand_dims(rain,2)
    rain = np.repeat(rain,3,2)

    rain_result = cv2.addWeighted(img,alpha,rain,1-alpha,1)
    #cv2.imshow('rain_effct',result)
    #cv2.waitKey()
    #cv2.destroyWindow('rain_effct')
    cv2.imwrite(os.path.join(out_dir, os.path.basename(img_name)), rain_result)


def process(img_name, out_dir, noise, rain_len, rain_angle, rain_thickness, alpha):
    # print(img_name, out_dir, noise, rain_len, rain_angle, rain_thickness, alpha)
    img = cv2.imread(img_name)
    noise = get_noise(img, value=noise)
    rain = rain_blur(noise, length=rain_len, angle=rain_angle, w=rain_thickness)
    alpha_rain(rain, img, img_name, out_dir, beta=alpha)
    #add_rain(rain, img, img_name, out_dir)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="dataset")

    parser.add_argument("--input_dir", type=str, default='H:\\0702\\1\\*.png')
    parser.add_argument("--output_dir", type=str, default='H:\\0702\\2\\')
    parser.add_argument("--noise", type=int, default=300) #100,150,200,250,300
    parser.add_argument("--rain_len", type=int, default=40) #20,30,40
    parser.add_argument("--rain_angle", type=int, default=20) #-40,-30,-20,-10,0,10,20,30,40
    parser.add_argument("--rain_thickness", type=int, default=5) #3,5,7
    parser.add_argument("--alpha", type=float, default=0.9) #0.9

    config = parser.parse_args()

    for file in glob.glob(config.input_dir):
        process(img_name = file,
                out_dir = config.output_dir,
                noise = random.randint(300, 500),
                rain_len = random.randint(20, 40),
                rain_angle = random.randint(-10, 40),
                rain_thickness = config.rain_thickness,
                alpha = config.alpha
                )
