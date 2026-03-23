# Plant Monitoring System Final Project (sorry, ik this is basic!)

## Overview

This project is an IoT system that monitors soil moisture levels in a plant and displays the data on a web dashboard. The system will helps user determine when their plant needs watering by alerting the user when the soil is dry. 

## Data Collected

* Soil moisture level
* Status (wet/dry)
* more specific data (i'm not too sure how i would determine the threshold)

## Hardware

* Raspberry Pi to read sensor data and send it over WiFi
* Soil moisture sensor to measure water content in the soil

## Functionality

* Reads soil moisture every 60 seconds
* Sends data to backend server
* Stores data in database
* Displays moisture trends on dashboard
* Alerts user when plant needs water


## System Architecture

Sensor → Raspberry Pi → Flask API → MongoDB → Web Dashboard


## The Web Dashboard will allow users to:

* View the current soil moisture level
* See a status indicator (e.g., “Plant is healthy” or “Water needed”)
* View a graph of moisture levels over time
* Monitor trends to understand how often the plant needs watering


## Security

* Token-based authentication for API requests

## Basic Goals

* Collect and store moisture data
* Display data on dashboard
* Indicate when plant is dry

## Future Goals

* Add temperature sensor
* Send alerts (email/notification)
* Real-time dashboard updates
* Cloud deployment with Docker
