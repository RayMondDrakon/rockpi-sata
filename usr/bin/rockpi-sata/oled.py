#!/usr/bin/python3
import time
import misc
import fan
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

font = {
    '10': ImageFont.truetype('fonts/DejaVuSansMono-Bold.ttf', 10),
    '11': ImageFont.truetype('fonts/DejaVuSansMono-Bold.ttf', 11),
    '12': ImageFont.truetype('fonts/DejaVuSansMono-Bold.ttf', 12),
    '14': ImageFont.truetype('fonts/DejaVuSansMono-Bold.ttf', 14),
}

misc.set_mode(23, 0)
time.sleep(0.2)
misc.set_mode(23, 1)


def disp_init():
    disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
    [getattr(disp, x)() for x in ('begin', 'clear', 'display')]
    return disp


try:
    disp = disp_init()
except Exception:
    misc.open_w1_i2c()
    time.sleep(0.2)
    disp = disp_init()

image = Image.new('1', (disp.width, disp.height))
draw = ImageDraw.Draw(image)


def disp_show():
    im = image.rotate(180) if misc.conf['oled']['rotate'] else image
    disp.image(im)
    disp.display()
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)


def welcome():
    draw.text((0, 0), 'ROCK Pi SATA HAT', font=font['14'], fill=255)
    draw.text((32, 16), 'Loading...', font=font['12'], fill=255)
    disp_show()


def goodbye():
    draw.text((30, 8), 'Power off...', font=font['14'], fill=255)
    disp_show()
    time.sleep(2)
    disp_show()  # clear


def put_disk_info():
    k, v = misc.get_disk_info()
    text1 = 'Disk: {} {}'.format(k[0], v[0])

    if len(k) == 5:
        text2 = '{} {}  {} {}'.format(k[1], v[1], k[2], v[2])
        text3 = '{} {}  {} {}'.format(k[3], v[3], k[4], v[4])
        page = [
            {'xy': (0, -2), 'text': text1, 'fill': 255, 'font': font['11']},
            {'xy': (0, 10), 'text': text2, 'fill': 255, 'font': font['11']},
            {'xy': (0, 21), 'text': text3, 'fill': 255, 'font': font['11']},
        ]
    elif len(k) == 4:
        text2 = '{} {}  {} {}'.format(k[1], v[1], k[2], v[2])
        text3 = '{} {}'.format(k[3], v[3])
        page = [
            {'xy': (0, -2), 'text': text1, 'fill': 255, 'font': font['11']},
            {'xy': (0, 10), 'text': text2, 'fill': 255, 'font': font['11']},
            {'xy': (0, 21), 'text': text3, 'fill': 255, 'font': font['11']},
        ]
    elif len(k) == 3:
        text2 = '{} {}  {} {}'.format(k[1], v[1], k[2], v[2])
        page = [
            {'xy': (0, 2), 'text': text1, 'fill': 255, 'font': font['12']},
            {'xy': (0, 18), 'text': text2, 'fill': 255, 'font': font['12']},
        ]
    elif len(k) == 2:
        text2 = '{} {}'.format(k[1], v[1])
        page = [
            {'xy': (0, 2), 'text': text1, 'fill': 255, 'font': font['12']},
            {'xy': (0, 18), 'text': text2, 'fill': 255, 'font': font['12']},
        ]
    else:
        page = [{'xy': (0, 2), 'text': text1, 'fill': 255, 'font': font['14']}]

    return page


def put_disk_io_info(pages_len):
    pages = {}
    page_index = pages_len
    disks = misc.get_disk_list('io_usage_mnt_points')

    for x in disks:
        x = misc.delete_disk_partition_number(x)

        pages[page_index] = [
            {'xy': (0, -2), 'text': 'Disk (' + x + '):', 'fill': 255, 'font': font['11']},
            {'xy': (0, 10), 'text': misc.get_disk_io_read_info(x), 'fill': 255, 'font': font['11']},
            {'xy': (0, 21), 'text': misc.get_disk_io_write_info(x), 'fill': 255, 'font': font['11']}
        ]
        page_index = page_index + 1

    return pages


def put_interface_info(pages_len):
    pages = {}
    page_index = pages_len
    interfaces = misc.get_interface_list()

    for x in interfaces:
        pages[page_index] = [
            {'xy': (0, -2), 'text': 'Network (' + x + '):', 'fill': 255, 'font': font['11']},
            {'xy': (0, 10), 'text': misc.get_interface_rx_info(x), 'fill': 255, 'font': font['11']},
            {'xy': (0, 21), 'text': misc.get_interface_tx_info(x), 'fill': 255, 'font': font['11']}
        ]
        page_index = page_index + 1

    return pages


def gen_pages():
    pages = {
        0: [
            {'xy': (0, -2), 'text': misc.get_info('up'), 'fill': 255, 'font': font['11']},
            {'xy': (0, 10), 'text': misc.get_cpu_temp(), 'fill': 255, 'font': font['11']},
            {'xy': (0, 21), 'text': misc.get_info('ip'), 'fill': 255, 'font': font['11']}
        ],
        1: [
            #{'xy': (0, 2), 'text': misc.get_info('cpu'), 'fill': 255, 'font': font['12']},
            #{'xy': (0, 18), 'text': misc.get_info('men'), 'fill': 255, 'font': font['12']}
            {'xy': (0, -2), 'text': 'Fan speed: ' + str(fan.get_dc()) + '%', 'fill': 255, 'font': font['11']},
            {'xy': (0, 10), 'text': misc.get_info('cpu'), 'fill': 255, 'font': font['11']},
            {'xy': (0, 21), 'text': misc.get_info('men'), 'fill': 255, 'font': font['11']},
        ],
        2: put_disk_info()
    }

    pages.update(put_interface_info(len(pages)))
    pages.update(put_disk_io_info(len(pages)))

    return pages


def slider(lock):
    with lock:
        for item in misc.slider_next(gen_pages()):
            draw.text(**item)
        disp_show()


def auto_slider(lock):
    while misc.conf['slider']['auto']:
        slider(lock)
        misc.slider_sleep()
    else:
        slider(lock)