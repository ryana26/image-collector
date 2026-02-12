#!/usr/bin/python3

import collections, cv2, numpy, os, pathlib, pyrealsense2 as rs2, PySimpleGUI as sg, subprocess, time, yaml
from datetime import datetime

directory = os.path.dirname(os.path.abspath(__file__))
gui_font = ('Arial', 12)
app_icon = directory + '/images/desktop_icon.png'

with open(pathlib.Path(__file__).parent / 'config.yaml') as file:
    config = yaml.load(file, Loader = yaml.FullLoader)

if config['capture_color_image'] == 1:
    capture_color_image = True
else:
    capture_color_image = False
if config['capture_infrared_image'] == 1:
    capture_infrared_image = True
else:
    capture_infrared_image = False
if config['capture_depth_image'] == 1:
    capture_depth_image = True
else:
    capture_depth_image = False
if config['input_weight'] == 1:
    input_weight = True
else:
    input_weight = False

fruit = config['fruit']
all_types = config['all_types']
type_keys = []
type_values = []
variety_keys = []
variety_values = []

# this function gets all the values out of the config list called all_types with the structure:
# all_types list > fruits list (e.g. grapes) > fruit types list (e.g. red grapes) > fruit varieties dictionary (e.g. flame)
def get_keys_and_values(fruit, all_types, type_keys, type_values, variety_keys, variety_values):
    # this for loop accesses each fruit list in the all_types list
    for fruit_name in all_types:
        # this for loop accesses each fruit type list in the fruit list
        for fruit_type in all_types[fruit_name]:
            # this checks that the fruit type is for the fruit the image collector is configured to take images for
            if fruit in fruit_type.replace(' ', '_').lower():
                # if the fruit type is for the correct fruit, its added to the type_keys and type_values lists
                type_keys.append(fruit_type.replace(' ', '_').lower())
                type_values.append(fruit_type)
                for variety in all_types[fruit_name][fruit_type]:
                    # the fruit varieties are added to the variety_keys and variety_values lists
                    variety_keys.append(variety)
                    variety_values.append(all_types[fruit_name][fruit_type][variety])

get_keys_and_values(fruit, all_types, type_keys, type_values, variety_keys, variety_values)

text_1 = fruit.title() + ' Types:'
text_2 = fruit.title() + ' Varieties:'
save_place = directory + '/images/' + fruit + '/'
defect_keys = list(config['defect_types'].keys())
defect_values = list(config['defect_types'].values())

CHECK_FOLDER = os.path.isdir(save_place)
if not CHECK_FOLDER: os.makedirs(save_place)

virtual_csv = []
csv_dict = {}

def csv_saver(csv):
    a = dict(collections.Counter(csv))

    for k, v in a.items():
        f = open(directory + '/image_details.csv', 'a')
        f.write(str(k) + ',' + str(v) + '\n'); f.close()

    with open(directory + '/image_details.csv') as f:
        for line in f.readlines():
            a, b = line.rsplit(',', maxsplit=1)
            b = b.split('\n')[0]
            global csv_dict
            if a in csv_dict: csv_dict[a] = int(csv_dict[a]) + int(b)
            else: csv_dict[a] = b

        os.remove(directory + '/image_details.csv')

        for x in csv_dict:
            f = open(directory + '/image_details.csv', 'a')
            f.write(str(x) + ',' + str(csv_dict[x]) + '\n'); f.close()

def save_images(fruit_type, fruit_variety, defect_type, weight):
    date_time = datetime.now().strftime('%d%m%Y-%H%M%S')
    device_product_line = str(device.get_info(rs2.camera_info.product_line))
    if input_weight:
        filename = f'{fruit_type}-{fruit_variety}-{defect_type}-{date_time}-{device_product_line}-{weight}'
    else:
        filename = f'{fruit_type}-{fruit_variety}-{defect_type}-{date_time}-{device_product_line}'

    if capture_color_image: cv2.imwrite(save_place + filename + '-color.jpg', color_image); print(
        f'Saving to {save_place}{filename}-color.jpg...')

    if capture_infrared_image:
        cv2.imwrite(save_place + filename + '-infrared.jpg', infrared_image)
        print(f'Saving to {save_place}{filename}-infrared.jpg...')

    if capture_depth_image:
        cv2.imwrite(save_place + filename + '-depth.jpg', depth_colormap)
        print(f'Saving to {save_place}{filename}-depth.jpg...')
        ply = rs2.save_to_ply(save_place + filename + '.ply')
        print(f'Saving to {save_place}{filename}.ply...')
        ply.set_option(rs2.save_to_ply.option_ply_binary, True)
        ply.set_option(rs2.save_to_ply.option_ply_normals, True)
        ply.process(frames)

    global virtual_csv
    csv_date = datetime.now().strftime('%Y/%m/%d')
    virtual_csv.append(str(csv_date) + ',' + str(fruit_type) + ',' + str(fruit_variety) + ',' + str(defect_type))

try:
    pipeline = rs2.pipeline()
    config = rs2.config()

    pipeline_wrapper = rs2.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs2.camera_info.product_line))

    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720

    if device_product_line == 'L500':
        DEPTH_WIDTH = 1024
        DEPTH_HEIGHT = 768
    else:
        DEPTH_WIDTH = 640
        DEPTH_HEIGHT = 480

    config.enable_stream(rs2.stream.depth, DEPTH_WIDTH, DEPTH_HEIGHT, rs2.format.z16, 30)
    config.enable_stream(rs2.stream.infrared, DEPTH_WIDTH, DEPTH_HEIGHT, rs2.format.y8, 30)
    config.enable_stream(rs2.stream.color, FRAME_WIDTH, FRAME_HEIGHT, rs2.format.bgr8, 30)

    profile = pipeline.start(config)

    #color_sensor = profile.get_device().query_sensors()[1]
    #color_sensor.set_option(rs2.option.exposure, 25)

    infra_sensor = profile.get_device().query_sensors()[0]
    infra_sensor.set_option(rs2.option.exposure, 10000)
    infra_sensor.set_option(rs2.option.laser_power, 0)

except Exception as e:
    print('Caught Exception:', e)
    sg.popup('Camera Not Connected!', title = '', font = gui_font, icon = app_icon)
    quit()

if input_weight:
    weight_layout = [sg.Text('Weight (g):', size = (13, 1)), sg.InputText(size = (26, 1))]
else:
    weight_layout = ''

layout1 = [
    [sg.Column([[sg.Button('Sync & Close', button_color = 'grey')]], element_justification = 'right', expand_x = True)],
    [sg.Text(text_1, size = (13, 1)), sg.Listbox(type_values, size = (26, 4), key = 1, enable_events = True)],
    [sg.Text(text_2, size = (13, 1)), sg.Listbox(variety_values, size = (26, 10), key = 2)],
    [sg.Text('Defect Type:', size = (13, 1)), sg.Listbox(defect_values, size = (26, 10), key = 3)],
    weight_layout,
    [sg.Column([[sg.Button('Take Picture', button_color = 'green')]], element_justification = 'right', expand_x = True)]]

layout = [[sg.Image(filename = '', key = 'camera_view', size = (400, 400)),
           sg.Column(layout1, element_justification = 'right', expand_x = True)]]

gui_window = sg.Window('Realsense Image Collector', layout, location = (10, 10), font = gui_font, resizable = True, enable_close_attempted_event = True, icon = app_icon, return_keyboard_events = True)

while True:
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    infrared_frame = frames.get_infrared_frame()
    if not depth_frame or not color_frame or not infrared_frame: continue

    color_image = numpy.asanyarray(color_frame.get_data())
    depth_image = numpy.asanyarray(depth_frame.get_data())
    infrared_image = numpy.asanyarray(infrared_frame.get_data())
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha = 0.1), cv2.COLORMAP_JET)

    depth_colormap_dim = depth_colormap.shape
    color_colormap_dim = color_image.shape

    event, values = gui_window.read(timeout = 20)

    if event == 1:
        fruit_type = type_keys[type_values.index(values[1][0])]
        gui_window[2].update(values = list(all_types[fruit][fruit_type.replace('_', ' ').title()].values()))

    if event == 'Sync & Close':
        csv_saver(virtual_csv)

        save_place_content = os.listdir(save_place)

        if len(save_place_content) > 0:
            sg.popup_non_blocking('Images are now syncing, please wait for program to close.', button_type = 5, title = '', font = gui_font, keep_on_top = True, icon = app_icon)
            print('running: ' + directory + '/upload.sh')
            subprocess.call(directory + '/upload.sh ' + fruit, shell = True)
        else:
            sg.popup_non_blocking('No images have been saved, program closing...', button_type = 5, title = '', font = gui_font, keep_on_top = True, icon = app_icon)
            time.sleep(1)
        break

    elif event == sg.WIN_CLOSED:
        break

    elif event == '-WINDOW CLOSE ATTEMPTED-':
        csv_saver(virtual_csv)

        save_place_content = os.listdir(save_place)

        if len(save_place_content) > 0:
            answer = sg.popup_yes_no('There are pictures that haven\'t been synced.', 'Are you sure you want to exit without syncing them?', title = 'Warning', font = gui_font, keep_on_top = True, icon = app_icon)
            if answer == 'Yes': break
        else:
            break

    elif event == 'Take Picture' or event == ' ' or event == 'space:65':
        try:
            fruit_type = type_keys[type_values.index(values[1][0])]
            fruit_variety = variety_keys[variety_values.index(values[2][0])]
            defect_type = defect_keys[defect_values.index(values[3][0])]
            if input_weight:
                weight = int(values[0])*1
                output_text = f'Fruit Type: {values[1][0]}\nFruit Variety: {values[2][0]}\nDefect Type: {values[3][0]}\nWeight: {weight}'
            else:
                weight = 0
                output_text = f'Fruit Type: {values[1][0]}\nFruit Variety: {values[2][0]}\nDefect Type: {values[3][0]}'
            sg.popup_timed(output_text, title = 'Image Details', font = gui_font, button_type = 5, auto_close_duration = 1, keep_on_top = True, icon = app_icon)
            save_images(fruit_type, fruit_variety, defect_type, weight)

        except Exception as e:
            print('Caught Exception:', e)
            sg.popup('All values required!', title = '', font = gui_font, keep_on_top = True, icon = app_icon)

    resized = cv2.resize(color_image, (900, 540))
    imgbytes = cv2.imencode('.png', resized)[1].tobytes()
    gui_window['camera_view'].update(data = imgbytes)

gui_window.close()
pipeline.stop()
