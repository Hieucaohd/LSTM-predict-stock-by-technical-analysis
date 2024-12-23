import sys
sys.path.append("../../")

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from pyspark import  SparkContext
from pyspark.sql import SparkSession
from ta import add_all_ta_features
from ta.utils import dropna
from utils.draw_candle_image import *
from generate_data.query_dataset import *
import json
import keras
import numpy as np
import numpy as np
import os
import pandas as pd
import random
import ta
import ta.momentum
import ta.trend
import ta.trend
import ta.volatility
import tensorflow as tf
from tabulate import tabulate


def generate_one_image_of_input(
    df_date: pd.DataFrame, 
    df_original: pd.DataFrame, 
    previous_days: int, 
    next_days: int,
    days_result: int,
    figscale: int,
    number_images_preview = 0,
    number_images_to_save = None,
    indicator = {}
    ):
    
    total_days = previous_days + 1 + next_days + days_result
    if len(df_date) < total_days:
        return
    
    count = 0
    total_images = df_date[Total_records][0]
    print(f"Total: {total_images} images")
    
    df_original = convert_number_index(df_original)
    
    list_images = []
    list_targets = []
    list_dates = []
    
    random_image_index_show = np.random.randint(0, total_images, size=number_images_preview)
    
    list_date_index_printed = []
    not_save_image_count = 0
    
    for date in df_date[Date_normalized]:
        date_index = get_date_index(df_original, date)
        
        count += 1
        if count % 100 == 0:
            print(f"Load {count}/{total_images} images")
            
        if len(list_date_index_printed) > 0:
            last_index_checked = list_date_index_printed[-1]
            if date_index - last_index_checked <= next_days:
                not_save_image_count += 1
                continue

        list_date_index_printed.append(date_index)
            
        if number_images_to_save is not None and count > number_images_to_save:
            break
        
        draw_df_pandas = add_days_around_date(date, df_original, previous_days, next_days)
        if len(draw_df_pandas) < (previous_days + next_days):
            continue
        
        is_preview_image = count in random_image_index_show
        image_tensor = draw_candle_image(
            draw_df_pandas, 
            show_x_y=False, 
            show_volume=False, 
            
            **indicator,
            
            figscale=figscale, 
            figcolor="black", 
            preview_image=is_preview_image,
            return_image_tensor=True
        )
        
        image_tensor = normalize_candle_image(
            image_tensor, 
            combine_into_one_image=False,
            convert_red=False,
            convert_green=False,
        )
        
        date = normalize_date(date)
        index_of_date = get_date_index(df_original, date)
        start_index = index_of_date - previous_days
        end_index = index_of_date + next_days + days_result
        data_result_df = df_original[start_index:end_index + 1]
    
        if 0 < len(data_result_df) < total_days:
            data_result_df = duplicate_last_row(data_result_df, total_days - len(data_result_df))
        elif len(data_result_df) == 0:
            continue
        
        targets = data_result_df[[High, Open, Close, Low]].to_numpy()
        
        list_images.append(image_tensor)
        list_targets.append(targets)
        list_dates.append(str(date))
    
    return list_images, list_targets, list_dates, not_save_image_count


def generate_two_image_of_input(
    df_date: pd.DataFrame, 
    df_original: pd.DataFrame, 
    previous_days: int, 
    next_days: int,
    days_result: int,
    figscale: int,
    number_images_preview = 0,
    number_images_to_save = None,
    indicator = {}
    ):
    
    total_days = previous_days + 1 + next_days + days_result
    if len(df_date) < total_days:
        return
    
    count = 0
    total_images = df_date[Total_records][0]
    print(f"Total: {total_images} images")
    
    df_original = convert_number_index(df_original)
    
    list_images = []
    list_targets = []
    list_dates = []
    
    random_image_index_show = np.random.randint(0, total_images, size=number_images_preview)
    
    list_date_index_printed = []
    not_save_image_count = 0
    
    for date in df_date[Date_normalized]:
        date_index = get_date_index(df_original, date)
        
        count += 1
        if count % 100 == 0:
            print(f"Load {count}/{total_images} images")
            
        if len(list_date_index_printed) > 0:
            last_index_checked = list_date_index_printed[-1]
            if date_index - last_index_checked <= next_days:
                not_save_image_count += 1
                continue

        list_date_index_printed.append(date_index)
            
        if number_images_to_save is not None and count > number_images_to_save:
            break
        
        draw_df_pandas = add_days_around_date(date, df_original, previous_days, next_days)
        if len(draw_df_pandas) < (previous_days + next_days):
            continue
        
        is_preview_image = count in random_image_index_show
        image_tensor = draw_candle_image(
            draw_df_pandas, 
            show_x_y=False, 
            show_volume=False, 
            
            **indicator,
            
            figscale=figscale, 
            figcolor="black", 
            preview_image=is_preview_image,
            return_image_tensor=True
        )
        
        image_tensor = normalize_candle_image(
            image_tensor, 
            combine_into_one_image=False,
            convert_red=False,
            convert_green=False,
        )
        
        date = normalize_date(date)
        index_of_date = get_date_index(df_original, date)
        start_index = index_of_date - previous_days
        end_index = index_of_date + next_days + days_result
        data_result_df = df_original[start_index:end_index + 1]
    
        if 0 < len(data_result_df) < total_days:
            data_result_df = duplicate_last_row(data_result_df, total_days - len(data_result_df))
        elif len(data_result_df) == 0:
            continue
        
        targets = data_result_df[[High, Open, Close, Low]].to_numpy()
        
        list_images.append(image_tensor)
        list_targets.append(targets)
        list_dates.append(str(date))
    
    return list_images, list_targets, list_dates, not_save_image_count


def save_to_tensorflow_dataset(
    df_date: pd.DataFrame, 
    df_original: pd.DataFrame, 
    previous_days: int, 
    next_days: int,
    days_result: int,
    figscale: int,
    number_images_preview = 0,
    save_dataset_to_folder = None,
    number_images_to_save = None,
    indicator = {},
    function_generate = None,
    ):
    
    list_images, list_targets, list_dates, not_print_image_count = function_generate(
        df_date,
        df_original,
        previous_days,
        next_days,
        days_result,
        figscale,
        number_images_preview,
        number_images_to_save,
        indicator,
    )
    
            
    list_images = np.array(list_images)
    list_targets = np.array(list_targets)
    list_dates = np.array(list_dates)
    
    print(f"Not print date: {not_print_image_count} images")
    print(f"list_images shape = {list_images.shape}")
    print(f"list_targets shape = {list_targets.shape}")
    
    dataset = tf.data.Dataset.from_tensor_slices((list_images, list_targets, list_dates))
    
    if save_dataset_to_folder is not None:
        if not os.path.exists(save_dataset_to_folder):
            os.makedirs(save_dataset_to_folder)
        else:
            exist_ok = input(f"Folder {save_dataset_to_folder} already exists, continue? [y/n]: ").lower()[0] == "y"
            if not exist_ok:
                return dataset
    
        tf.data.Dataset.save(dataset, save_dataset_to_folder)
    
    return dataset
