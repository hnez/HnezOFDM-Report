from PIL import Image, ImageDraw
import numpy as np


FFT_LEN= 16
ZOOM= 8

def export(src, name):
    src_re, src_im= src

    sx, sy= src_im.shape

    img= Image.new('RGB', (sy, sx) , 'black')
    pixels= img.load()

    for x in range(sx):
        for y in range(sy):
            r= 0
            g= int(src_im[x, y] * 255)
            b= int(src_re[x, y] * 255)

            pixels[y, x]= (r, g, b)

    scaled= img.resize((sy * 4, sx * 4))

    grid= Image.new('RGB', scaled.size, 'black')

    draw= ImageDraw.Draw(grid)
    scx, scy= grid.size

    for x in range(0, FFT_LEN):
        draw.line(((x*32+14, 0), (x*32+14, scy)), fill=255)
        draw.line(((x*32+18, 0), (x*32+18, scy)), fill=255)

        draw.line(((0, x*32+14), (scx, x*32+14)), fill=255)
        draw.line(((0, x*32+18), (scx, x*32+18)), fill=255)

    scaled.save('{}_wf.png'.format(name))
    grid.save('{}_grid.png'.format(name))

def waterfall(src):
    pad= np.zeros(FFT_LEN)
    padded= np.concatenate((pad, src, pad, pad))

    stride_len= FFT_LEN // ZOOM

    chunks= list(
        np.concatenate((
            src[start:start+FFT_LEN],
            np.zeros(FFT_LEN * (ZOOM - 1))
        ))
        for start
        in range(0, len(src) - FFT_LEN, stride_len)
    )

    fqd= np.stack(tuple(
        np.fft.fft(chunk)
        for chunk in chunks
    ))

    fqd_re= fqd.real
    fqd_im= fqd.imag

    minv= min(fqd_re.min(), fqd_im.min())
    maxv= max(fqd_re.max(), fqd_im.max())

    fqd_re= (fqd_re - minv) / (maxv - minv)
    fqd_im= (fqd_im - minv) / (maxv - minv)

    return (fqd_re, fqd_im)

def gen_ofdm_sym(len_fft):
    fqd= np.random.choice((-1, 1), len_fft) + np.random.choice((-1j, 1j), len_fft)
    tid= np.fft.ifft(fqd)

    return tid


frame= np.concatenate(tuple(
    gen_ofdm_sym(FFT_LEN)
    for i in range(FFT_LEN)
))

export(waterfall(frame), 'ofdm_sync_vis')
export(waterfall(np.clip(frame, -0.05, 0.05)), 'ofdm_sync_vis_nonlinear')
