# steganographics
A pure-python steganography library for hiding data in image, video and audio files


secret_img = image_to_bin(path) #image to hide

img = LSB(secret_img) #use Least Significant Bit method

img.hide(secret_img,new_path)

###

i = LSB(new_path)

secret_data = i.read()

bin_to_image(secret_data,recovered_image_path)
